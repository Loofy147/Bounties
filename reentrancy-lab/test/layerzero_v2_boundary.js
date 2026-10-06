const assert = require("assert");
const ganache = require("ganache");
const { ethers } = require("ethers");
const solc = require("solc");
const fs = require("fs");
const path = require("path");

function compile() {
  const file = path.join(__dirname, "..", "contracts", "layerzero_v2", "LayerZeroV2Boundary.sol");
  const source = fs.readFileSync(file, "utf8");
  const input = {
    language: "Solidity",
    sources: { "LayerZeroV2Boundary.sol": { content: source } },
    settings: { outputSelection: { "*": { "*": ["abi", "evm.bytecode.object"] } } },
  };
  const output = JSON.parse(solc.compile(JSON.stringify(input)));
  const errors = (output.errors || []).filter((e) => e.severity === "error");
  if (errors.length) throw new Error(errors.map((e) => e.formattedMessage).join("\n"));
  return output.contracts["LayerZeroV2Boundary.sol"];
}

function artifact(compiled, name) {
  return {
    abi: compiled[name].abi,
    bytecode: "0x" + compiled[name].evm.bytecode.object,
  };
}

async function expectRevert(promise, label) {
  try {
    await promise;
    throw new Error(label + ": expected revert");
  } catch (err) {
    if (String(err.message).includes("expected revert")) throw err;
  }
}

async function main() {
  const compiled = compile();
  const provider = new ethers.providers.Web3Provider(
    ganache.provider({ wallet: { totalAccounts: 5 }, logging: { quiet: true } })
  );
  const accounts = await provider.listAccounts();
  const owner = provider.getSigner(accounts[0]);
  const attacker = provider.getSigner(accounts[1]);
  const endpointSigner = provider.getSigner(accounts[2]);

  const Endpoint = new ethers.ContractFactory(
    artifact(compiled, "MockEndpointV2").abi,
    artifact(compiled, "MockEndpointV2").bytecode,
    endpointSigner
  );
  const endpoint = await Endpoint.deploy();
  await endpoint.deployed();

  const Secure = new ethers.ContractFactory(
    artifact(compiled, "BoundaryReceiver").abi,
    artifact(compiled, "BoundaryReceiver").bytecode,
    owner
  );
  const secure = await Secure.deploy(endpoint.address);
  await secure.deployed();

  const MutantEndpoint = new ethers.ContractFactory(
    artifact(compiled, "Mutant_NoEndpointGate").abi,
    artifact(compiled, "Mutant_NoEndpointGate").bytecode,
    owner
  );
  const mutantEndpoint = await MutantEndpoint.deploy(endpoint.address);
  await mutantEndpoint.deployed();

  const MutantPeer = new ethers.ContractFactory(
    artifact(compiled, "Mutant_NoPeerGate").abi,
    artifact(compiled, "Mutant_NoPeerGate").bytecode,
    owner
  );
  const mutantPeer = await MutantPeer.deploy(endpoint.address);
  await mutantPeer.deployed();

  const MutantReplay = new ethers.ContractFactory(
    artifact(compiled, "Mutant_NoReplayGuard").abi,
    artifact(compiled, "Mutant_NoReplayGuard").bytecode,
    endpointSigner
  );
  const mutantReplay = await MutantReplay.deploy();
  await mutantReplay.deployed();

  const ReplaySecure = new ethers.ContractFactory(
    artifact(compiled, "BoundaryReceiver").abi,
    artifact(compiled, "BoundaryReceiver").bytecode,
    owner
  );
  const replaySecure = await ReplaySecure.deploy(mutantReplay.address);
  await replaySecure.deployed();

  const srcEid = 30101;
  const trustedPeer = ethers.utils.hexZeroPad(accounts[3], 32);
  const wrongPeer = ethers.utils.hexZeroPad(accounts[4], 32);
  const guid = ethers.utils.hexZeroPad("0x01", 32);
  const message = ethers.utils.hexZeroPad(ethers.utils.hexlify(1234), 32);
  const executor = accounts[2];
  const extraData = "0x";

  for (const c of [secure, mutantEndpoint, mutantPeer, replaySecure]) {
    await (await c.setPeer(srcEid, trustedPeer)).wait();
  }

  const originGood = { srcEid, sender: trustedPeer, nonce: 1 };
  const originWrongPeer = { srcEid, sender: wrongPeer, nonce: 2 };

  // Secure boundary: valid endpoint + valid peer reaches application logic.
  await (await endpoint.deliver(
    secure.address, originGood, guid, message, executor, extraData
  )).wait();
  assert.strictEqual((await secure.receiveCount()).toString(), "1");
  assert.strictEqual((await secure.lastAmount()).toString(), "1234");

  // Secure boundary: direct caller cannot impersonate Endpoint.
  await expectRevert(
    secure.connect(attacker).lzReceive(
      originGood, guid, message, executor, extraData
    ),
    "secure endpoint gate"
  );

  // Secure boundary: even the real Endpoint cannot spoof the configured peer.
  await expectRevert(
    endpoint.deliver(
      secure.address, originWrongPeer, guid, message, executor, extraData
    ),
    "secure peer gate"
  );

  // Secure channel: the same (receiver, srcEid, sender, nonce) cannot deliver twice.
  await expectRevert(
    endpoint.deliver(
      secure.address, originGood, guid, message, executor, extraData
    ),
    "secure replay guard"
  );

  // Mutant A: deleting the Endpoint gate creates an attacker-reachable state transition.
  await (await mutantEndpoint.connect(attacker).lzReceive(
    originGood, guid, message, executor, extraData
  )).wait();
  assert.strictEqual((await mutantEndpoint.receiveCount()).toString(), "1");

  // Mutant B: deleting the Peer gate accepts an untrusted source sender.
  await (await endpoint.deliver(
    mutantPeer.address, originWrongPeer, guid, message, executor, extraData
  )).wait();
  assert.strictEqual((await mutantPeer.receiveCount()).toString(), "1");

  // Mutant C: deleting the channel replay guard permits the same packet nonce twice.
  await (await mutantReplay.deliverUnchecked(
    replaySecure.address, originGood, guid, message, executor, extraData
  )).wait();
  await (await mutantReplay.deliverUnchecked(
    replaySecure.address, originGood, guid, message, executor, extraData
  )).wait();
  assert.strictEqual((await replaySecure.receiveCount()).toString(), "2");

  console.log("PASS secure endpoint gate");
  console.log("PASS secure peer gate");
  console.log("PASS secure replay/channel gate");
  console.log("KILLED mutant: missing endpoint gate");
  console.log("KILLED mutant: missing peer gate");
  console.log("KILLED mutant: missing replay guard");
  console.log("RESULT LayerZeroV2Boundary = PASS");
}

main().catch((err) => {
  console.error(err.stack || err);
  process.exit(1);
});
