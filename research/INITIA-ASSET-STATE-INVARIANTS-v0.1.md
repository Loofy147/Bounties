# Runtime State-Integrity Monitoring for MoveVM Assets — v0.1

**Status:** Detection specification / no implementation or runtime experiment performed  
**Origin:** Initia incident discussed in `targets/initia/INCIDENT-SNAPSHOT-2026-10-25.md`  
**Goal:** Detect unexplained spendable-balance changes and cross-domain reserve releases by checking state-write provenance, not merely user-visible events.

## 1. Detection objective

Alert when a transaction's successful execution produces an asset balance delta that cannot be reconciled with the asset's documented authorized operations and state-transition accounting model.

The detector should be implemented close enough to the VM/adapter storage boundary to observe actual state writes. Event-only monitoring is insufficient if the failure mode bypasses or corrupts the path that normally emits supply/mint events.

## 2. Required evidence per observed state mutation

Record, when available:
- chain ID, height, transaction hash, transaction index, and execution result;
- pre-state and post-state digest;
- resource/table key and asset type;
- account/resource owner;
- old/new balance or value digest (store raw amounts only where permitted);
- executing module, function/script identity, call stack or execution trace ID;
- resolved authorization/capability decision;
- supply-counter delta and relevant mint/burn events;
- related escrow, bridge-message, nonce, and redemption records;
- cache hit/miss and cache/session lifecycle metadata, if the runtime exposes them.

A log entry without enough provenance to reconstitute the state delta is a weak signal, not proof.

## 3. Invariants

### RI-1 — Authorized positive balance delta

For every spendable-balance increase, there must be a documented source:
- transfer from a source balance with a matching debit;
- authorized mint path with correct authority and supply effects;
- authorized bridge mint/release path with the required authenticated message/backing evidence;
- genesis, migration, reward, or protocol exception explicitly documented for this chain.

A MoveVM cache or state-management path itself should not be treated as asset-creation authority.

### RI-2 — Asset-model-specific conservation

For each concrete asset type, formalize its actual balance/supply relationship. Do not universalize `sum(account balances) = total supply` when protocol reserves, burns, escrow, or framework-specific accounting can affect the equation.

The monitor must flag:
- an account balance increase with no authorized source;
- supply/balance deltas inconsistent with the declared asset model;
- a mint/burn authority mismatch;
- a resource/table mutation bypassing the expected accounting operation.

The incident reports that account balances were assigned while total supply stayed unchanged; that particular combination is a signal to investigate, not a full invariant definition without the actual asset module semantics.

### RI-3 — Cache state isolation

For a given transaction input and state snapshot, warm-cache and cold-cache paths must make equivalent validation decisions and produce equivalent state effects.

A cache entry must not carry an authorization result, sender context, transaction argument, type argument, or state-dependent assumption into a transaction where that data differs. The exact legitimate cache key/validation context must be established from source and design; the detector must not guess the historical root cause.

### RI-4 — Cross-domain redemption

A reserve release on chain B must be explainable by the protocol's expected authenticated state transition originating from chain A. Join the records using the bridge-specific message identifier/nonce, asset identity, amount, destination, and replay/finality semantics.

Flag:
- reserve release without expected burn/redeem evidence;
- message nonce or identifier reuse;
- mismatch between source asset and destination reserve asset;
- amount mismatch between source transition and reserve release;
- redemption backed only by a spendable balance whose state-write provenance is anomalous.

## 4. Rule candidates

These are implementation-level detector rules, not executable SIEM syntax.

| Rule ID | Predicate | Response |
|---|---|---|
| RI-AUTH-01 | Spendable balance increased; no recognized authorized source transition exists | Critical integrity alert; preserve trace; pause only under pre-approved response policy |
| RI-SUPPLY-02 | Balance/supply/reserve deltas violate the asset-specific invariant | Critical integrity alert; independently replay state transition |
| RI-CACHE-03 | Same transaction/state has different validation or state result between warm-cache and cold-cache execution in a controlled regression environment | Release-blocking test failure |
| RI-BRIDGE-04 | External reserve release lacks the required matching source evidence or has inconsistent amount/asset/nonce | Critical bridge accounting alert |
| RI-TRACE-05 | State write cannot be attributed to a module/function/authorized operation class | High/critical observability gap; do not assume exploitation until validated |

Use exact severity only after defining the system's response model and impact; the table's labels are triage priorities, not bounty severity assignments.

## 5. False-positive controls

Before alerting, account for:
- explicitly authorized genesis and migration writes;
- protocol rewards, fee accrual, rebases, and supply changes with special semantics;
- vault/resource accounts and bridge escrow;
- delayed cross-chain finality and message ordering;
- batched transactions, rollback/abort behavior, and multi-step transitions;
- assets whose “total supply” counter is intentionally not the sum of user balances;
- differences caused by nondeterministic metadata that do not alter security-relevant state.

Where a full invariant cannot be calculated from available telemetry, emit “unexplained delta / insufficient evidence” rather than a confirmed exploit alert.

## 6. Validation plan

1. Build a normal execution baseline for each asset implementation.
2. Add seeded, test-only unauthorized state mutations and verify RI-AUTH-01 / RI-SUPPLY-02 fire.
3. Add legitimate mint, transfer, burn, fee, migration, and bridge-redemption controls to measure false positives.
4. Test abort/rollback, repeated messages, resource account, and batch boundaries.
5. Compare cache-hot/cache-cold outcomes only in a controlled test runtime.
6. Replay the same recorded trace with independent state accounting; compare event and storage deltas.
7. Record detection precision, recall, false-positive rate, evidence completeness, and detection latency. Do not claim performance until benchmarked.

## 7. Non-goals and safety

- This document has no live-chain connection and executes no transactions.
- It does not define a production response that automatically halts the chain.
- It does not establish a vulnerability or a bounty-eligible target.
- It must not be used to test Initia or a bridge without current explicit authorization.
