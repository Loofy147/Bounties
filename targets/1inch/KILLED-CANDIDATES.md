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

## K-04 — Undercollateralized resolver reward as profitable extraction

Observation: For C < R, a resolver can supply T = R-C WETH so the clone balance reaches the reward R, leaving zero cancellation proceeds for the maker.

Static disposition: KILLED FOR PROFITABILITY / technical mechanism remains EXPERIMENTALLY_SUPPORTED.

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

The measured gas total for deposit + transfer + cancellation is:

    51,951 + 29,443 + 56,627 = 138,021 gas.

At the 10 gwei base fee used for the reward calculation, this is already:

    138,021 * 10 gwei = 0.00138021 ETH

which exceeds the maximum reward:

    R = 0.00077 ETH

Therefore, for C < R, even the limiting case T -> 0 cannot make the resolver profitable through this top-up strategy under the measured current-code gas path. At the observed 11 gwei effective gas price, the corresponding cost is approximately 0.001518231 ETH, before considering any additional opportunity/capital cost.

This kills the prior claim that C > cancellation-only gas was a sufficient profitability condition. The technical behavior remains real, but the examined economic extraction path is not a rational positive-return attack under the measured cost envelope.

Re-open condition: obtain a materially lower verified execution-cost path, a reward parameter/configuration that changes the bound, or another mechanism that transfers additional victim value without requiring equivalent resolver funding.

## Current frontier

H-E2 remains useful as a technical accounting observation, but its current undercollateralized-profit sub-hypothesis is KILLED.

Do not submit K-04 as a bounty finding without a new positive-impact mechanism.

Audit/known-issue reconciliation and resolver eligibility remain separate OPEN gates for any residual H-E2 interpretation.
