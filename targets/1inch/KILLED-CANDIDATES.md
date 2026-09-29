# 1inch Limit Order Protocol — Killed Candidate Register

Snapshot: 2026-09-29
Working target: `4.3.4` → `7da29889efa2e635611e1caf60f85f595ff7f05f`

These are deliberately preserved negative results from static review. They are not vulnerability reports.

## K-01 — Factory accepts non-WETH maker asset

Observation: `NativeOrderFactory.create()` checks maker, receiver, and `msg.value == makingAmount`, but does not require `makerAsset == WETH`.

Static disposition: **KILLED / non-impactful as currently understood**.

Reason: the factory deposits the supplied native value as WETH into the clone regardless of the signed `makerAsset`. If the order names another maker asset, the resulting order is ordinarily unfillable because the clone holds WETH rather than that asset. The creator is the party supplying the native value and must also be the order maker, so the observed effect is creator-controlled self-denial, not an apparent unauthorized transfer.

Re-open condition: demonstrate a sequence where a third party can cause another user's native collateral to be transferred, trapped, or economically consumed through this mismatch.

## K-02 — Maker `withdraw()` can drain active native collateral

Observation: `NativeOrderImpl.withdraw()` permits the maker to execute an arbitrary call with ETH value from the clone. Existing upstream tests explicitly exercise maker withdrawal of the clone's WETH.

Static disposition: **KILLED / intentional behavior unless a state/authorization bypass is found**.

Reason: withdrawal is protected by both `onlyMaker(makerOrder.maker)` and `validateOrder(makerOrder)`, the latter recomputing the deterministic clone from the supplied original order. A maker withdrawing its own collateral can make that order unfillable, but the current code does not expose an identified cross-maker or cross-clone path.

Re-open condition: demonstrate cross-order or cross-maker withdrawal, or a way to pass validation for a different clone/order.

## K-03 — Resolver reward greater than remaining WETH balance

Observation: the calculated resolver reward can exceed the clone's current WETH balance, after which `balance -= resolverReward` reverts.

Static disposition: **KILLED / caller-induced revert**.

Reason: the resolver controls `rewardLimit` and can request zero reward. The arithmetic failure prevents cancellation rather than transferring excess funds, so the current behavior is a failed caller request, not an identified theft or privilege escalation.

Re-open condition: demonstrate that an attacker can force an otherwise valid resolver cancellation to fail in a way that produces an in-scope economic or availability impact beyond the resolver's own transaction.

## Current frontier

The active native-order hypotheses remain H-E1 (ERC-1271 clone/hash relation), H-E2 (collateral/cancellation accounting), and H-F1 (Permit2Proxy authorization boundary).

Execution status remains **UNKNOWN / OPEN**; these dispositions are static-analysis results only.