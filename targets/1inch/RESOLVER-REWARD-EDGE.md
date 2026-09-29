
# NativeOrder Resolver Reward / Total-Balance Edge

Snapshot: 2026-09-29
Target: 1inch Limit Order Protocol 4.3.4
Commit: 7da29889efa2e635611e1caf60f85f595ff7f05f
Status: EXPERIMENTALLY_SUPPORTED / CANDIDATE OPEN

## Observation

NativeOrderImpl._cancelOrder() reads the clone's entire WETH balance, unwraps it, then subtracts the resolver reward before paying the remainder to the maker.

Thus, any WETH already resident in the clone is part of the balance from which the resolver reward is funded.

## Reproduced controls

Run #32 (36522991905), research commit 75f8dfde597a408e28d6e633dad6ea9c805833bc, completed SUCCESS with four controls:

- NativeOrder ERC-1271 boundary
- same-maker clone isolation
- resolver reward total-balance behavior
- undercollateralized resolver reward behavior

The undercollateralized control used:

- maker collateral C = 0.0001 ETH
- reward cap R = 0.00077 ETH at 10 gwei
- resolver top-up R-C = 0.00067 ETH

It established that the resolver cancellation can consume the maker's residual clone collateral once the missing reward balance is supplied locally.

## Victim-impact calibration

A dedicated calibration control on research head e39993268632cc0b758ec7be98cd31048699949c completed successfully in run #51 (job 109265719467).

Measured values:

- C = 0.0007 ETH
- R = 0.00077 ETH
- T = 0.00007 ETH
- cancellation gas = 56,627
- effective gas price = 11 gwei
- cancellation gas cost = 0.000622897 ETH
- maker-side cancellation loss = 0.0007 ETH
- resolver reward = 0.00077 ETH

The calibration is deliberately a victim-loss test, not a profitability claim.

## Natural residual-state evidence

The upstream 4.3.4 test suite contains an ETH-maker-order partial-fill case:

- initial native collateral: 0.3 ETH-equivalent WETH;
- first fill: 0.2;
- residual clone balance: 0.1 WETH;
- maker cancellation refunds the residual 0.1 WETH.

Therefore residual clone collateral after partial fill is a normal protocol state.

Our dedicated partial-fill control reproduces the same state transition with a residual C below the resolver reward cap, then successfully executes resolver cancellation after expiry plus the configured delay.

## Full economic accounting

The resolver's true end-to-end economics must count:

    reward = top-up + deposit gas + transfer gas + cancellation gas + net gain

Earlier shorthand based only on cancellation gas was incomplete and is no longer treated as a profitability result.

Run #64 completed the remaining execution and produced complete resolver-side accounting.

## Design-intent evidence

Upstream PR #390 explicitly discussed whether the whole WETH balance should be returned to the maker, including accidentally deposited WETH. The maintainer stated that this full-balance behavior was intentional.

This is evidence of conscious full-balance semantics. It is not evidence that the undercollateralized resolver interaction was previously recognized.

## Eligibility / adversary model

ESTABLISHED: the resolver is a permissioned operational actor and the intended caller of resolver cancellation.

The current program's privileged-address wording names governance and strategist. Current Immunefi guidance states that where a program provides such a list, only the addresses enumerated by that rule are treated as privileged for that exclusion. Resolver is not enumerated. This narrows, but does not by itself finish, the eligibility question.

## Audit / known-issue gate

The official 1inch audit archive contains a v4.3.4 OpenZeppelin report entry, but the archive material currently associated with that entry describes the Permit2Proxy extension.

Current evidence therefore does not establish that NativeOrderFactory/NativeOrderImpl were covered by that particular v4.3.4 audit. This is an evidence gap, not evidence that NativeOrder was never reviewed elsewhere.

No explicit prior source-text disclosure of the tested undercollateralized reward condition has been found in the targeted GitHub search performed so far. Absence is not novelty proof.

## Promotion conditions

Promote beyond EXPERIMENTALLY_SUPPORTED / ELIGIBILITY OPEN only when all are established:

1. Resolver/access-token-holder is accepted as an adversary under current bounty rules.
2. The behavior maps to an in-scope user-fund impact.
3. No applicable audit or known issue already discloses the same behavior.
4. A minimal victim scenario is established under permitted local-fork conditions.
5. Full end-to-end resolver economics are characterized without incomplete cost assumptions.

Final state: the technical, natural-state, and full-cost gates are ESTABLISHED by run #64. Audit/known-issue, production-version correspondence, and minimum production victim-state gates remain OPEN. Do not assign severity or bounty amount yet.
