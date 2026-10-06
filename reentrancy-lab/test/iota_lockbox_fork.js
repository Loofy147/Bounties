#!/usr/bin/env node
"use strict";

const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");
const { ethers } = require("ethers");

const TARGET = "0xAEf027F94008430BF4Fc27FFABB49ea6F1dd3414";
const ENDPOINT = "0x1a44076050125825900e736c501f859c50fe728c";
const USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7";
const PEER =
  "0xe6a11eb6a514b5510d731e5ed9d8e9294bcaad3b4696fa5d45406d11560b5902";
const RECEIVE_LIB =
  "0xc02Ab410f0734EFa3F14628780e6e695156024C2";
const IMPLEMENTATION =
  "0x1ab288f49e18884b3a5358f4079ca0f40b891d99";
const LOCAL_RPC = "http://127.0.0.1:8545";
const RPC_URL =
  process.env.ALCHEMY_ETH_RPC ||
  "https://eth-mainnet.g.alchemy.com/public";

const BLOCKS = {
  config: Number(process.env.CONFIG_FORK_BLOCK || 25989160),
  unlock: Number(process.env.UNLOCK_FORK_BLOCK || 26133519),
};

const EIP1967_IMPL_SLOT =
  "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc";

const ENDPOINT_ABI = [
  "function eid() view returns (uint32)",
  "function getReceiveLibrary(address,uint32) view returns (address,bool)",
  "function defaultReceiveLibrary(uint32) view returns (address)",
  "function receiveLibraryTimeout(address,uint32) view returns (address,uint256)",
];

const TARGET_ABI = [
  "function endpoint() view returns (address)",
  "function owner() view returns (address)",
  "function peers(uint32) view returns (bytes32)",
  "function lzReceive((uint32,uint64,bytes32),bytes32,bytes,address,bytes) payable",
  "function setPeer(uint32,bytes32)",
];

const ULN_ABI = [
  "function getUlnConfig(address,uint32) view returns (tuple(uint64 confirmations,uint8 requiredDVNCount,uint8 optionalDVNCount,uint8 optionalDVNThreshold,address[] requiredDVNs,address[] optionalDVNs))",
];

const ERC20_ABI = [
  "function balanceOf(address) view returns (uint256)",
  "function decimals() view returns (uint8)",
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function waitForRpc(provider, timeoutMs = 15000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      await provider.getBlockNumber();
      return;
    } catch (_) {
      await new Promise((r) => setTimeout(r, 250));
    }
  }
  throw new Error("Anvil RPC did not become ready");
}

async function startAnvil(blockNumber) {
  const child = spawn(
    "anvil",
    [
      "--fork-url",
      RPC_URL,
      "--fork-block-number",
      String(blockNumber),
      "--host",
      "127.0.0.1",
      "--port",
      "8545",
      "--silent",
    ],
    { stdio: ["ignore", "pipe", "pipe"] }
  );

  const log = [];
  child.stdout.on("data", (b) => log.push(b.toString()));
  child.stderr.on("data", (b) => log.push(b.toString()));

  await waitForRpc(new ethers.providers.JsonRpcProvider(LOCAL_RPC));

  return {
    child,
    stop() {
      if (!child.killed) child.kill("SIGTERM");
    },
    log() {
      return log.join("").slice(-4000);
    },
  };
}

async function impersonate(provider, address) {
  await provider.send("anvil_setBalance", [
    address,
    "0x3635C9ADC5DEA0000000000000", // 1e24 wei
  ]);
  await provider.send("anvil_impersonateAccount", [address]);
  return provider.getSigner(address);
}

async function main() {
  const mode = process.env.TEST_MODE || "config";
  if (!BLOCKS[mode]) throw new Error(`unknown TEST_MODE=${mode}`);

  const blockNumber = BLOCKS[mode];
  const outDir = path.resolve(__dirname, "../../artifacts/iota-lockbox-fork");
  fs.mkdirSync(outDir, { recursive: true });

  const anvil = await startAnvil(blockNumber);
  const provider = new ethers.providers.JsonRpcProvider(LOCAL_RPC);

  try {
    const network = await provider.getNetwork();
    assert(network.chainId === 1, "fork chainId must be Ethereum mainnet");

    const observedBlock = await provider.getBlockNumber();
    assert(
      observedBlock === blockNumber,
      `fork block mismatch: got ${observedBlock}, expected ${blockNumber}`
    );

    const target = new ethers.Contract(TARGET, TARGET_ABI, provider);
    const endpoint = new ethers.Contract(ENDPOINT, ENDPOINT_ABI, provider);
    const usdt = new ethers.Contract(USDT, ERC20_ABI, provider);

    const [implementationRaw, endpointAddress, owner, peer, endpointEid] =
      await Promise.all([
        provider.getStorageAt(TARGET, EIP1967_IMPL_SLOT),
        target.endpoint(),
        target.owner(),
        target.peers(30423),
        endpoint.eid(),
      ]);

    const implementation = ethers.utils.getAddress(
      "0x" + implementationRaw.slice(-40)
    );

    const [receiveLib, defaultLib, timeout] = await Promise.all([
      endpoint.getReceiveLibrary(TARGET, 30423),
      endpoint.defaultReceiveLibrary(30423),
      endpoint.receiveLibraryTimeout(TARGET, 30423),
    ]);

    const effective = ethers.utils.getAddress(receiveLib[0]);
    const isDefault = receiveLib[1];

    assert(ethers.utils.getAddress(implementation) === ethers.utils.getAddress(IMPLEMENTATION),
      `implementation mismatch: ${implementation}`);
    assert(ethers.utils.getAddress(endpointAddress) === ethers.utils.getAddress(ENDPOINT),
      `endpoint mismatch: ${endpointAddress}`);
    assert(peer.toLowerCase() === PEER.toLowerCase(), "peer mismatch");
    assert(endpointEid === 30101, `endpoint EID mismatch: ${endpointEid}`);
    assert(effective.toLowerCase() === RECEIVE_LIB.toLowerCase(), "receive library mismatch");
    assert(ethers.utils.getAddress(defaultLib).toLowerCase() === RECEIVE_LIB.toLowerCase(),
      "default receive library mismatch");
    assert(
      timeout[0] === ethers.constants.AddressZero && timeout[1].eq(0),
      "unexpected active receive-library timeout"
    );

    const lockboxBalanceBefore = await usdt.balanceOf(TARGET);

    const evidence = {
      mode,
      block: blockNumber,
      target: TARGET,
      implementation,
      endpoint: endpointAddress,
      endpointEid,
      owner,
      peer,
      receiveLibrary: effective,
      receiveLibraryIsDefault: isDefault,
      defaultReceiveLibrary: defaultLib,
      receiveLibraryTimeout: {
        library: timeout[0],
        expiry: timeout[1].toString(),
      },
      lockboxUsdtBefore: lockboxBalanceBefore.toString(),
      rpcSource: RPC_URL.includes("/public") ? "ALCHEMY_PUBLIC" : "ALCHEMY_PRIVATE_ENV",
      localForkOnly: true,
    };

    if (mode === "config") {
      assert(lockboxBalanceBefore.eq(0), "pinned config block should have zero lockbox USDT");
      const out = path.join(outDir, "config.json");
      fs.writeFileSync(out, JSON.stringify(evidence, null, 2) + "\n");
      console.log("PASS pinned config state reproduced");
      console.log("PASS implementation / endpoint / peer / library / timeout checks");
      console.log(`ARTIFACT ${out}`);
      return;
    }

    const attacker =
      "0x1000000000000000000000000000000000000001";
    const badPeer =
      "0x" + "00".repeat(12) + "1111111111111111111111111111111111111111";

    const attackerSigner = await impersonate(provider, attacker);
    const targetAsAttacker = target.connect(attackerSigner);

    let attackerRejected = false;
    try {
      const tx = await targetAsAttacker.setPeer(30423, badPeer, {
        gasLimit: 500000,
      });
      await tx.wait();
    } catch (_) {
      attackerRejected = true;
    }
    assert(attackerRejected, "UNAUTHORIZED OWNER MUTATION DID NOT REVERT");

    const endpointSigner = await impersonate(provider, ENDPOINT);
    const targetAsEndpoint = target.connect(endpointSigner);

    const guid = ethers.utils.hexZeroPad("0x01", 32);
    const recipient = "0x2000000000000000000000000000000000000002";
    const amount = ethers.BigNumber.from(1_000_000); // 1 USDT
    const message = ethers.utils.solidityPack(
      ["bytes32", "uint64"],
      [ethers.utils.hexZeroPad(recipient, 32), amount]
    );

    const wrongOrigin = {
      srcEid: 30423,
      nonce: 1,
      sender: badPeer,
    };

    let wrongPeerRejected = false;
    try {
      const tx = await targetAsEndpoint.lzReceive(
        wrongOrigin,
        guid,
        message,
        attacker,
        "0x",
        { gasLimit: 1_500_000 }
      );
      await tx.wait();
    } catch (_) {
      wrongPeerRejected = true;
    }
    assert(wrongPeerRejected, "WRONG PEER MESSAGE DID NOT REVERT");

    const recipientBefore = await usdt.balanceOf(recipient);
    const lockboxBefore = await usdt.balanceOf(TARGET);

    assert(lockboxBefore.gte(amount), "unlock test requires >= 1 USDT on lockbox");

    const validOrigin = {
      srcEid: 30423,
      nonce: 1,
      sender: PEER,
    };

    const validTx = await targetAsEndpoint.lzReceive(
      validOrigin,
      guid,
      message,
      attacker,
      "0x",
      { gasLimit: 1_500_000 }
    );
    const receipt = await validTx.wait();

    const recipientAfter = await usdt.balanceOf(recipient);
    const lockboxAfter = await usdt.balanceOf(TARGET);

    assert(
      recipientAfter.sub(recipientBefore).eq(amount),
      "valid endpoint+peer did not release exact amount"
    );
    assert(
      lockboxBefore.sub(lockboxAfter).eq(amount),
      "lockbox balance delta != recipient delta"
    );

    evidence.unlockTest = {
      attackerRejected,
      wrongPeerRejected,
      validMessageTx: receipt.transactionHash,
      recipient,
      amount: amount.toString(),
      recipientBefore: recipientBefore.toString(),
      recipientAfter: recipientAfter.toString(),
      lockboxBefore: lockboxBefore.toString(),
      lockboxAfter: lockboxAfter.toString(),
    };

    const out = path.join(outDir, "unlock.json");
    fs.writeFileSync(out, JSON.stringify(evidence, null, 2) + "\n");

    console.log("PASS unauthorized owner mutation rejected");
    console.log("PASS wrong peer rejected at target boundary");
    console.log("PASS endpoint+correct peer released exactly 1 USDT on LOCAL FORK");
    console.log(`ARTIFACT ${out}`);
  } finally {
    anvil.stop();
    if (anvil.log()) console.error(anvil.log());
  }
}

main().catch((err) => {
  console.error(err.stack || err);
  process.exit(1);
});
