# 1inch Limit Order Protocol — Killed Candidate Register

Snapshot: 2026-09-29
Working target: 4.3.4 -> 7da29889efa2e635611e1caf60f85f595ff7f05f

These are deliberately preserved negative results. They are not vulnerability reports.

## K-01 — Factory accepts non-WETH maker asset

Observation: NativeOrderFactory.create() checks maker, receiver, and msg.value == makingAmount, but does not require makerAsset == WETH.

Static disposition: KILLED / non-impactful as currently understood.

Reason: the factory deposits the supplied native value as WETH into the clone regardless of the signed makerAsset. If the order names another maker asset, the resulting order is ordinarily unfillable because the clone holds WETH rather than that asset. The creator is the party supplying the native value and must also be the order maker, so the observed effect is creator-controlled self-denial, not an apparent unauthorized transfer.

Re-open condition: demonstrate a sequence where a third party can cause another user's native collateral to be transferred, trapped, or economically consumed through this mismatch.

## K-02 — Maker withdraw() can drain active native collateral

Observation: NativeOrderImpl.withdraw() permits the maker to execute an arbitrary call with ETH value from the clone. Existing upstream tests explicitly exercise maker withdrawal of the clone's WETH.

Static disposition: KILLED / intentional behavior unless a state/authorization bypass is found.

Reason: withdrawal is protected by both onlyMaker(makerOrder.maker) and validateOrder(makerOrder), the latter recomputing the deterministic clone from the supplied original order. A maker withdrawing its own collateral can make that order unfillable, but the current code does not expose an identified cross-maker or cross-clone path.

Re-open condition: demonstrate cross-order or cross-maker withdrawal, or a way to pass validation for a different clone/order.

## K-03 — Resolver reward greater than remaining WETH balance

Observation: the calculated resolver reward can exceed the clone's current WETH balance, after which balance -= resolverReward reverts.

Static disposition: KILLED / caller-induced revert.

Reason: the resolver controls rewardLimit and can request zero reward. The arithmetic failure prevents cancellation rather than transferring excess funds, so the current behavior is a failed caller request, not an identified theft or privilege escalation.

Re-open condition: demonstrate that an attacker can force an otherwise valid resolver cancellation to fail in a way that produces an in-scope economic or availability impact beyond the resolver's own transaction.

## K-04 — Undercollateralized resolver reward extraction (REOPENED)

Observation: For C < R, a resolver can supply T = R-C WETH so the clone balance reaches the reward R, leaving zero cancellation proceeds for the maker.

Static disposition: REOPENED / technical mechanism remains EXPERIMENTALLY_SUPPORTED.

Evidence:
- successful victim-loss calibration on run #51, job 109265719467, head e39993268632cc0b758ec7be98cd31048699949c;
- C = 0.0007 ETH;
- R = 0.00077 ETH;
- T = 0.00007 ETH;
- cancellation gas = 56,627;
- effective gas price = 11 gwei;
- cancellation gas cost = 0.000622897 ETH;
- WETH deposit gas measured = 51,951;
- WETH transfer gas measured = 29,443.

Historical profitability check: the measured gas total for deposit + transfer + cancellation was:

    51,951 + 29,443 + 56,627 = 138,021 gas.

At the 10 gwei base fee used for the reward calculation, this is already:

    138,021 * 10 gwei = 0.00138021 ETH

which exceeds the maximum reward R = 0.00077 ETH in that historical calibration. That correctly showed the chosen top-up path was negative-EV under those measured local costs.

However, the profitability-only kill is retired. Current Immunefi guidance treats attacker financial risk/ROI as a feasibility consideration and does not make low ROI alone a sufficient reason to invalidate or downgrade the underlying bug. The completed natural partial-fill execution measured victim loss 0.0007 ETH and resolver net loss 0.00006743195654982 ETH, so attacker loss was about 9.63% of victim loss in the demonstrated case.

The mechanism therefore remains open pending the other eligibility and production gates.

Re-open condition is satisfied by the final natural partial-fill execution; remaining closure conditions are audit/known-issue reconciliation, resolver-role rule interpretation, production version correspondence, and minimum production victim state.

## Current frontier

H-E2 is EXPERIMENTALLY_SUPPORTED. K-04 is REOPENED. Do not assign severity or submit until the remaining audit/known-issue, resolver-role, production-version, and victim-state gates are resolved.

Audit/known-issue reconciliation and resolver eligibility remain separate OPEN gates for any residual H-E2 interpretation.
