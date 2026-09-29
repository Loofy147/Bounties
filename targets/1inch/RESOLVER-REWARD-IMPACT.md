# NativeOrder Resolver Reward — Economic Impact Calibration

Snapshot: 2026-09-29
Target: 1inch Limit Order Protocol 4.3.4
Commit: `7da29889efa2e635611e1caf60f85f595ff7f05f`

## Exact accounting model

Let:

- (C) = maker-owned WETH balance in the clone immediately before resolver cancellation;
- (T) = resolver-owned WETH top-up transferred to the clone before cancellation;
- (B=C+T) = total clone WETH balance, assuming no other balance component;
- (R=min(rewardLimit,; block.basefee	imes70,000	imes1.1)).

The cancellation path reads the full clone balance, unwraps it, then pays (R) to the resolver and (B-R) to the maker.

The operation succeeds only when (Bge R).

For the undercollateralized case (C<R), choose (T=R-C). Then:

[
B=R
]

[
	ext{maker proceeds}=B-R=0
]

[
	ext{resolver gross proceeds}=R
]

[
	ext{resolver top-up}=R-C
]

Before gas:

[
	ext{resolver net}=R-(R-C)=C
]

Therefore:

[
oxed{	ext{maker loss}=C}
]

and

[
oxed{	ext{resolver net after top-up and gas}=C-G}
]

where (G) is the actual cancellation transaction gas cost.

In other words, the reproduced mechanism can consume **100% of the maker's residual clone collateral** when (C<R).

## 10 gwei calibration

For the current 4.3.4 reward cap:

[
R=70,000	imes10	ext{ gwei}	imes1.1
=0.00077	ext{ ETH}
]

Run #32 reports a `cancelExpiredOrderByResolver` gas figure of 56,603 for the undercollateralized control.

At 10 gwei:

[
G=56,603	imes10	ext{ gwei}
=0.00056603	ext{ ETH}
]

Representative points:

| Maker collateral (C) | Resolver top-up (R-C) | Maker loss | Resolver net after gas* |
|---:|---:|---:|---:|
| 0.0001 ETH | 0.00067 ETH | 0.0001 ETH | -0.00046603 ETH |
| 0.0006 ETH | 0.00017 ETH | 0.0006 ETH | +0.00003397 ETH |
| 0.0007 ETH | 0.00007 ETH | 0.0007 ETH | +0.00013397 ETH |
| (C	o R) | (R-C	o0) | (C	o0.00077) ETH | (	o0.00020397) ETH |

*Using the observed 56,603-gas calibration at 10 gwei; the exact net depends on the transaction's effective gas price.

The original (C=0.0001) behavioral reproduction is therefore deliberately **not profitable** at 10 gwei. It proves the transfer mechanism. Economic viability begins when (C>G).

## General break-even

In the pure undercollateralized/top-up model:

[
oxed{C>G}
]

is the resolver-profitability condition.

If the effective gas price is approximately the base fee, the reward-cap headroom is approximately:

[
R-Gapprox(77,000-56,603)	imes block.basefee
=20,397	imes block.basefee
]

Thus under this model:

- maximum gross maker loss for one targeted residual balance is bounded by (R);
- maximum resolver net is approximately (R-G), before priority fees and any other capital/opportunity cost;
- across multiple independently cancellable clones, the aggregate loss is the sum of each targeted (C_i) satisfying the attack conditions.

## Important boundary

This is an **impact characterization**, not a severity determination.

Eligibility still depends on:
- whether a resolver/access-token holder is an allowed adversary;
- whether this use of the resolver reward path is an unintended security property;
- whether the same behavior appears in applicable audits or prior disclosures;
- whether a real victim state is reachable under permitted local-fork conditions.

The dedicated economic-calibration test was added at:
`Loofy147/limit-order-protocol:test/BountyResolverRewardEconomicCalibration.js`

Its CI execution is pending run #38.

No severity or bounty amount is assigned here.
