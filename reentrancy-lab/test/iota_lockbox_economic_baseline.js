#!/usr/bin/env node
"use strict";

/*
 * Read-only historical invariant check.
 *
 * This test never submits or simulates a state-changing transaction.
 * It samples already-mined Lockbox USDT transfers and requires each sample
 * to contain the corresponding OFTReceived and Endpoint PacketDelivered
 * records with matching recipient, amount, source EID, and configured peer.
 */

const { ethers } = require("ethers");

const RPC_URL =
  process.env.ALCHEMY_ETH_RPC ||
  "https://eth-mainnet.g.alchemy.com/public";

const LOCKBOX =
  "0xAEf027F94008430BF4Fc27FFABB49ea6F1dd3414".toLowerCase();
const ENDPOINT =
  "0x1a44076050125825900e736c501f859c50fe728c".toLowerCase();
const USDT =
  "0xdAC17F958D2ee523a2206206994597C13D831ec7".toLowerCase();
const PEER =
  "0xe6a11eb6a514b5510d731e5ed9d8e9294bcaad3b4696fa5d45406d11560b5902".toLowerCase();

const ERC20_TRANSFER =
  "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef";
const OFT_RECEIVED =
  "0xefed6d3500546b29533b128a29e3a94d70788727f0507505ac12eaf2e578fd9c";
const PACKET_DELIVERED =
  "0x3cd5e48f9730b129dc7550f0fcea9c767b7be37837cd10e55eb35f734f4bca04";

const SAMPLES = [
  {
    hash: "0x025014e33ce434e4dfea05d8b03ebac9308084bc44cb6c3cef4abcea974dc28e",
    to: "0xf51cff050f1079e9db735090731c33d39d768ece",
    amount: "15730266080"
  },
  {
    hash: "0x9a251a09feca4e86f2c80e7da1327c212973469c917a082dfddb2dcf0ba1931c",
    to: "0x6e59426c652c87060fc0378e1181a5013b0251fb",
    amount: "500000000"
  },
  {
    hash: "0xb72559dd23bffe2a575ce2e231b6d1659983eda39f4cb66f1e7ab629bff54936",
    to: "0xfb602a96d5dea984d768b38629a93a73125936e0",
    amount: "1000000"
  },
  {
    hash: "0xf993eade000f6348bdf89922f5862fa08af3a66643fdea3a986ddec0ad34c603",
    to: "0xcf6b14efb50691982724251e0e94641b4526feea",
    amount: "5000000"
  },
  {
    hash: "0x2579e2d97a196a8225712d937338d82b9d5b06583993cbfeb1908fb817ec3048",
    to: "0x1eb3fb84f28cdf2690b10c99281a21ffde0f3183",
    amount: "10000000"
  },
  {
    hash: "0xca1641bb1a1f9e4885f02e4fbdbd01f801113963c732d9595d32b15ca7029ac6",
    to: "0xcf6b14efb50691982724251e0e94641b4526feea",
    amount: "5000000"
  },
  {
    hash: "0x3b20c935bcb048a77ddd03e68bc0b8dcb33c097d53c88f68f49decd3820f62cc",
    to: "0x1eb3fb84f28cdf2690b10c99281a21ffde0f3183",
    amount: "10000000"
  },
  {
    hash: "0xa4a418abdc9c26e8f6d4f0a4c23860bb3e90d1dfca39e68bd93ca774bcfa5992",
    to: "0x7de5c505f7cb10f476d1e2dbe4816a6b71238354",
    amount: "5000000"
  },
  {
    hash: "0x34d6f130b7097ed71324ef75a177876ccc59af2528931d3dbd9bd1569ff6a357",
    to: "0x1a303003d92b274596b14e4d888d08934f3f05de",
    amount: "115588508"
  },
  {
    hash: "0xc2ce401ac3ac8a0d61b9bc9f0a5edbcdb22b6cf4590f98c0ca8e208783c8f3a",
    to: "0xf51cff050f1079e9db735090731c33d39d768ece",
    amount: "5000000"
  }
];

function stripAddress(topic) {
  return ethers.utils.getAddress("0x" + topic.slice(-40)).toLowerCase();
}

function uint256Word(data, index) {
  const start = 2 + index * 64;
  return ethers.BigNumber.from("0x" + data.slice(start, start + 64));
}

function bytes32Word(data, index) {
  const start = 2 + index * 64;
  return "0x" + data.slice(start, start + 64);
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function main() {
  const provider = new ethers.providers.JsonRpcProvider(RPC_URL);
  const network = await provider.getNetwork();
  assert(network.chainId === 1, "RPC must point to Ethereum mainnet");

  const results = [];

  for (const sample of SAMPLES) {
    const receipt = await provider.getTransactionReceipt(sample.hash);
    assert(receipt, "missing receipt: " + sample.hash);
    assert(receipt.status === 1, "sample transaction failed: " + sample.hash);

    const target = receipt.logs.find(
      (l) =>
        l.address.toLowerCase() === USDT &&
        l.topics[0].toLowerCase() === ERC20_TRANSFER &&
        stripAddress(l.topics[1]) === LOCKBOX &&
        stripAddress(l.topics[2]) === sample.to
    );

    const received = receipt.logs.find(
      (l) =>
        l.address.toLowerCase() === LOCKBOX &&
        l.topics[0].toLowerCase() === OFT_RECEIVED &&
        stripAddress(l.topics[2]) === sample.to
    );

    const delivered = receipt.logs.find(
      (l) =>
        l.address.toLowerCase() === ENDPOINT &&
        l.topics[0].toLowerCase() === PACKET_DELIVERED
    );

    assert(target, "ERC20 Transfer missing: " + sample.hash);
    assert(received, "OFTReceived missing: " + sample.hash);
    assert(delivered, "PacketDelivered missing: " + sample.hash);

    const erc20Amount = ethers.BigNumber.from(target.data);
    const srcEid = uint256Word(received.data, 0).toNumber();
    const oftAmount = uint256Word(received.data, 1);
    const packetSrcEid = uint256Word(delivered.data, 0).toNumber();
    const packetPeer = bytes32Word(delivered.data, 1).toLowerCase();
    const packetReceiver = ethers.utils.getAddress(
      "0x" + delivered.data.slice(-40)
    ).toLowerCase();

    assert(erc20Amount.eq(sample.amount), "ERC20 amount mismatch: " + sample.hash);
    assert(oftAmount.eq(sample.amount), "OFTReceived amount mismatch: " + sample.hash);
    assert(srcEid === 30423, "OFTReceived srcEid mismatch: " + sample.hash);
    assert(packetSrcEid === 30423, "PacketDelivered srcEid mismatch: " + sample.hash);
    assert(packetPeer === PEER, "PacketDelivered peer mismatch: " + sample.hash);
    assert(packetReceiver === LOCKBOX, "PacketDelivered receiver mismatch: " + sample.hash);

    results.push({
      hash: sample.hash,
      block: receipt.blockNumber,
      recipient: sample.to,
      amountRaw: sample.amount,
      amountUSDT: ethers.utils.formatUnits(sample.amount, 6),
      invariant: "ERC20 Transfer == OFTReceived == PacketDelivered"
    });
  }

  console.log(JSON.stringify({
    status: "PASS",
    sample_count: results.length,
    established_in_sample: {
      source_eid: 30423,
      peer: PEER,
      recipient_consistency: true,
      amount_consistency: true,
      endpoint_delivery_evidence: true
    },
    samples: results
  }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error);
  process.exit(1);
});
