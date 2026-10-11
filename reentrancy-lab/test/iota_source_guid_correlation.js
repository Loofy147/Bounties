#!/usr/bin/env node
"use strict";

/*
 * Read-only cross-chain message correlation.
 *
 * For the already-mined Ethereum Lockbox outflow sample:
 *   1. reads Ethereum receipts from the existing RPC,
 *   2. extracts the PacketDelivered origin tuple,
 *   3. recomputes the official LayerZero V2 GUID,
 *   4. pages through IOTA L1 OFTSentEvent records,
 *   5. requires GUID + destination EID + amount correspondence.
 *
 * This script never sends transactions, mutates production state, or
 * impersonates an account. Ethereum and IOTA sources are read-only.
 */

const fs = require("fs");
const path = require("path");
const { ethers } = require("ethers");

const RPC_URL =
  process.env.ALCHEMY_ETH_RPC ||
  "https://eth-mainnet.g.alchemy.com/public";
const IOTA_GRAPHQL_URL =
  process.env.IOTA_L1_GRAPHQL_URL ||
  "https://graphql.mainnet.iota.cafe/graphql";

const LOCKBOX = "0xaef027f94008430bf4fc27ffabb49ea6f1dd3414";
const ENDPOINT = "0x1a44076050125825900e736c501f859c50fe728c";
const USDT = "0xdac17f958d2ee523a2206206994597c13d831ec7";
const SOURCE_EID = 30423;
const DESTINATION_EID = 30101;
const PEER =
  "0xe6a11eb6a514b5510d731e5ed9d8e9294bcaad3b4696fa5d45406d11560b5902";
const PACKET_DELIVERED =
  "0x3cd5e48f9730b129dc7550f0fcea9c767b7be37837cd10e55eb35f734f4bca04";
const OFT_SENT_TYPE = PEER + "::oft::OFTSentEvent";

const PAGE_SIZE = 100;
const MAX_PAGES = 100;
const STOP_PADDING_SECONDS = 24 * 60 * 60;

const EVIDENCE_PATH = path.resolve(
  __dirname,
  "../../targets/usdt0/evidence/2026-10-06-iota-lockbox-economic-baseline.json"
);
const OUTPUT_DIR = path.resolve(__dirname, "../../artifacts/iota-lockbox-fork");
const OUTPUT_PATH = path.join(OUTPUT_DIR, "cross-chain-guid-correlation.json");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function word(data, index) {
  const start = 2 + index * 64;
  return "0x" + data.slice(start, start + 64);
}

function bigintWord(data, index) {
  return ethers.BigNumber.from(word(data, index));
}

function normalizeSample(row) {
  if (Array.isArray(row)) {
    return {
      hash: row[0],
      block: Number(row[1]),
      recipient: row[2].toLowerCase(),
      amountRaw: String(row[3])
    };
  }
  return {
    hash: row.hash,
    block: Number(row.block),
    recipient: row.recipient.toLowerCase(),
    amountRaw: String(row.amountRaw)
  };
}

function normalizeGuid(value) {
  if (typeof value === "string") {
    const normalized = value.startsWith("0x") ? value.toLowerCase() : "0x" + value.toLowerCase();
    return /^0x[0-9a-f]{64}$/.test(normalized) ? normalized : null;
  }
  if (Array.isArray(value) && value.length === 32 && value.every(Number.isInteger)) {
    return "0x" + Buffer.from(value).toString("hex");
  }
  if (value && typeof value === "object") {
    if (Array.isArray(value.bytes)) return normalizeGuid(value.bytes);
    if (Array.isArray(value.data)) return normalizeGuid(value.data);
    if (Array.isArray(value.value)) return normalizeGuid(value.value);
  }
  return null;
}

function eventInteger(value) {
  if (value === null || value === undefined) return null;
  if (typeof value === "number") return value;
  if (typeof value === "string" && /^\d+$/.test(value)) return Number(value);
  return null;
}

async function queryIotaEvents(before) {
  const query = `
    query SourceOftSends($pageSize: Int!, $cursor: String, $eventType: String!) {
      events(
        last: $pageSize,
        before: $cursor,
        filter: { eventType: $eventType }
      ) {
        edges {
          cursor
          node {
            timestamp
            json
            transactionBlock { digest }
          }
        }
        pageInfo {
          hasPreviousPage
          startCursor
        }
      }
    }
  `;
  const response = await fetch(IOTA_GRAPHQL_URL, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      accept: "application/graphql-response+json, application/json"
    },
    body: JSON.stringify({
      query,
      variables: {
        pageSize: PAGE_SIZE,
        cursor: before || null,
        eventType: OFT_SENT_TYPE
      }
    })
  });
  const text = await response.text();
  assert(response.ok, "IOTA GraphQL HTTP " + response.status + ": " + text.slice(0, 800));
  let body;
  try {
    body = JSON.parse(text);
  } catch (_) {
    throw new Error("IOTA GraphQL returned non-JSON: " + text.slice(0, 800));
  }
  assert(!body.errors || body.errors.length === 0,
    "IOTA GraphQL query error: " + JSON.stringify(body.errors || []).slice(0, 1600));
  assert(body.data && body.data.events, "IOTA GraphQL response missing data.events");
  return body.data.events;
}

async function main() {
  const baseline = JSON.parse(fs.readFileSync(EVIDENCE_PATH, "utf8"));
  const samples = baseline.samples.map(normalizeSample);
  assert(samples.length === 15, "expected 15 baseline samples, got " + samples.length);

  const provider = new ethers.providers.JsonRpcProvider(RPC_URL);
  const network = await provider.getNetwork();
  assert(network.chainId === 1, "RPC must point to Ethereum mainnet");

  const ethPackets = [];
  for (const sample of samples) {
    const receipt = await provider.getTransactionReceipt(sample.hash);
    assert(receipt, "missing Ethereum receipt: " + sample.hash);
    assert(receipt.status === 1, "Ethereum receipt failed: " + sample.hash);
    const delivered = receipt.logs.find(
      (log) =>
        log.address.toLowerCase() === ENDPOINT &&
        log.topics[0] &&
        log.topics[0].toLowerCase() === PACKET_DELIVERED
    );
    assert(delivered, "PacketDelivered missing: " + sample.hash);
    assert((delivered.data.length - 2) === 64 * 4,
      "unexpected PacketDelivered data length: " + sample.hash);

    const sourceEid = bigintWord(delivered.data, 0).toNumber();
    const sender = word(delivered.data, 1).toLowerCase();
    const nonce = bigintWord(delivered.data, 2);
    const receiverAddress = ethers.utils.getAddress(
      "0x" + delivered.data.slice(-40)
    ).toLowerCase();
    assert(sourceEid === SOURCE_EID,
      "unexpected source EID for " + sample.hash + ": " + sourceEid);
    assert(sender === PEER, "unexpected peer in " + sample.hash + ": " + sender);
    assert(receiverAddress === LOCKBOX,
      "unexpected receiver in " + sample.hash + ": " + receiverAddress);

    // Official LayerZero V2 GUID formula:
    // keccak256(abi.encodePacked(nonce, srcEid, sender, dstEid, receiverBytes32)).
    const guid = ethers.utils.keccak256(
      ethers.utils.solidityPack(
        ["uint64", "uint32", "bytes32", "uint32", "bytes32"],
        [
          nonce,
          sourceEid,
          sender,
          DESTINATION_EID,
          ethers.utils.hexZeroPad(LOCKBOX, 32)
        ]
      )
    ).toLowerCase();
    const block = await provider.getBlock(receipt.blockNumber);
    assert(block, "missing Ethereum block metadata: " + sample.hash);

    ethPackets.push({
      ethereumTx: sample.hash,
      ethereumBlock: receipt.blockNumber,
      ethereumTimestamp: block.timestamp,
      recipient: sample.recipient,
      amountRaw: sample.amountRaw,
      sourceEid,
      sender,
      nonce: nonce.toString(),
      destinationEid: DESTINATION_EID,
      receiver: LOCKBOX,
      guid
    });
  }

  // Independent regression vector calculated from the observed first receipt:
  // nonce=1888, srcEid=30423, sender=IOTA peer, dstEid=30101, receiver=Lockbox.
  const regression = ethPackets.find(
    (p) => p.ethereumTx ===
      "0x025014e33ce434e4dfea05d8b03ebac9308084bc44cb6c3cef4abcea974dc28e"
  );
  assert(regression,
    "GUID regression transaction was not found in the normalized 15-sample set");
  assert(regression.nonce === "1888",
    "GUID regression nonce mismatch: observed=" + regression.nonce +
      " srcEid=" + regression.sourceEid +
      " sender=" + regression.sender +
      " receiver=" + regression.receiver +
      " guid=" + regression.guid);
  assert(regression.guid ===
    "0x992b3595a78d6667723dd18fb49aac721ddeac04aebcdecdd21851c43cc6ff38",
    "GUID formula regression mismatch: nonce=" + regression.nonce +
      " srcEid=" + regression.sourceEid +
      " sender=" + regression.sender +
      " receiver=" + regression.receiver +
      " guid=" + regression.guid);

  const wanted = new Map(ethPackets.map((p) => [p.guid, p]));
  const matched = new Map();
  const pageSummaries = [];
  let cursor = null;
  let scanned = 0;
  let stoppedByTimeWindow = false;
  const oldestEthereumTimestamp = Math.min(...ethPackets.map((p) => p.ethereumTimestamp));
  const cutoff = oldestEthereumTimestamp - STOP_PADDING_SECONDS;

  for (let pageNumber = 1; pageNumber <= MAX_PAGES; pageNumber += 1) {
    const connection = await queryIotaEvents(cursor);
    const edges = connection.edges || [];
    const nodes = edges.map((edge) => edge.node);
    if (nodes.length === 0) break;

    const parsed = nodes.map((node) => {
      const json = node.json || {};
      return {
        timestamp: node.timestamp,
        timestampSeconds: Math.floor(new Date(node.timestamp).getTime() / 1000),
        transactionDigest: node.transactionBlock && node.transactionBlock.digest,
        guid: normalizeGuid(json.guid),
        dstEid: eventInteger(json.dst_eid ?? json.dstEid),
        amountSent: json.amount_sent_ld ?? json.amountSentLd ?? null,
        amountReceived: json.amount_received_ld ?? json.amountReceivedLd ?? null,
        jsonGuidShape: json.guid === undefined ? typeof json.guid :
          (Array.isArray(json.guid) ? "array" : typeof json.guid)
      };
    });
    assert(parsed.every((p) => Number.isFinite(p.timestampSeconds)),
      "IOTA event returned a non-parseable timestamp");
    scanned += parsed.length;

    for (const p of parsed) {
      if (!p.guid || !wanted.has(p.guid)) continue;
      const eth = wanted.get(p.guid);
      const amountReceived = p.amountReceived === null ? null : String(p.amountReceived);
      const amountSent = p.amountSent === null ? null : String(p.amountSent);
      if (p.dstEid !== null) {
        assert(p.dstEid === DESTINATION_EID,
          "matched GUID has unexpected OFTSentEvent dstEid: " + p.guid);
      }
      if (amountReceived !== null) {
        assert(amountReceived === eth.amountRaw,
          "matched GUID has amount_received_ld mismatch for " + eth.ethereumTx +
          ": IOTA=" + amountReceived + " Ethereum=" + eth.amountRaw);
      }
      matched.set(p.guid, {
        guid: p.guid,
        iotaSourceTx: p.transactionDigest,
        iotaSourceTimestamp: p.timestamp,
        iotaDstEid: p.dstEid,
        iotaAmountSentRaw: amountSent,
        iotaAmountReceivedRaw: amountReceived,
        ethereumTx: eth.ethereumTx,
        ethereumBlock: eth.ethereumBlock,
        ethereumTimestamp: eth.ethereumTimestamp,
        recipient: eth.recipient,
        amountRaw: eth.amountRaw
      });
    }

    const minPageTime = Math.min(...parsed.map((p) => p.timestampSeconds));
    const maxPageTime = Math.max(...parsed.map((p) => p.timestampSeconds));
    pageSummaries.push({
      page: pageNumber,
      count: parsed.length,
      oldestTimestamp: new Date(minPageTime * 1000).toISOString(),
      newestTimestamp: new Date(maxPageTime * 1000).toISOString(),
      sampleGuidMatchesInPage: parsed.filter((p) => p.guid && wanted.has(p.guid)).length,
      guidFieldShapeSamples: [...new Set(parsed.slice(0, 5).map((p) => p.jsonGuidShape))]
    });

    if (minPageTime <= cutoff) {
      stoppedByTimeWindow = true;
      break;
    }
    if (!connection.pageInfo || !connection.pageInfo.hasPreviousPage ||
        !connection.pageInfo.startCursor) {
      break;
    }
    cursor = connection.pageInfo.startCursor;
  }

  const correlations = ethPackets.map((p) => {
    const match = matched.get(p.guid);
    return {
      ...p,
      match: match || null
    };
  });

  const matchedCount = correlations.filter((p) => p.match).length;
  const result = {
    status: matchedCount === ethPackets.length ? "PASS" : "INCOMPLETE",
    test: "LZ-CROSSCHAIN-GUID-CORRELATION-01",
    claim: "Each sampled Ethereum Lockbox unlock is correlated by LayerZero GUID to a source-side IOTA L1 OFTSentEvent when that source event is in the scanned time window.",
    source: {
      chain: "IOTA L1 mainnet",
      endpoint: IOTA_GRAPHQL_URL,
      eventType: OFT_SENT_TYPE,
      destinationEid: DESTINATION_EID
    },
    destination: {
      chain: "Ethereum mainnet",
      lockbox: LOCKBOX,
      endpoint: ENDPOINT,
      sourceEid: SOURCE_EID,
      peer: PEER
    },
    scan: {
      queryPages: pageSummaries.length,
      eventsScanned: scanned,
      pageSize: PAGE_SIZE,
      maxPages: MAX_PAGES,
      timeWindowCutoff: new Date(cutoff * 1000).toISOString(),
      stoppedByTimeWindow,
      note: "Read-only GraphQL event query; no target transactions were submitted."
    },
    sampleCount: ethPackets.length,
    correlatedCount: matchedCount,
    uncorrelatedEthereumTransactions: correlations.filter((p) => !p.match).map((p) => ({
      ethereumTx: p.ethereumTx,
      guid: p.guid,
      timestamp: new Date(p.ethereumTimestamp * 1000).toISOString()
    })),
    pageSummaries,
    correlations
  };

  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(result, null, 2) + "\n");
  console.log(JSON.stringify({
    status: result.status,
    test: result.test,
    sampleCount: result.sampleCount,
    correlatedCount: result.correlatedCount,
    eventsScanned: result.scan.eventsScanned,
    queryPages: result.scan.queryPages,
    cutoff: result.scan.timeWindowCutoff,
    stoppedByTimeWindow: result.scan.stoppedByTimeWindow,
    uncorrelated: result.uncorrelatedEthereumTransactions,
    evidencePath: OUTPUT_PATH
  }, null, 2));
  assert(matchedCount === ethPackets.length,
    "source/destination GUID correlation incomplete: " + matchedCount + "/" + ethPackets.length);
}

main().catch((error) => {
  console.error(error.stack || error);
  process.exit(1);
});
