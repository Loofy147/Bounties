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
	ext{resolver capital spent on top-up}=R-C
]

Before gas:

[
	ext{resolver net}=R-(R-C)=C
]

So the reproduced victim loss is exactly (C), while resolver net economics are:

[
	ext{resolver net}=C-G
]

where (G) is the actual cancellation transaction gas cost.

## 10 gwei calibration

For the current 4.3.4 cap:

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

Therefore:

- (C=0.0001) ETH → resolver net (approx-0.00046603) ETH;
- (C=0.0006) ETH → resolver net (approx+0.00003397) ETH;
- (C=0.0007) ETH → resolver net (approx+0.00013397) ETH;
- as (C	o R), resolver net approaches (R-G=0.00020397) ETH.

The (C=0.0001) scenario used for behavioral reproduction is therefore **not economically profitable** for the resolver at 10 gwei. It establishes the transfer mechanism, not economic viability.

## General break-even condition

With actual gas cost (G):

[
C>G
]

is the resolver profitability condition in the pure undercollateralized/top-up model.

Using the contract's reward cap and actual gas consumption, the approximate headroom before priority-fee effects is:

[
R-G
approx
(77,000-56,603)	imes block.basefee
=20,397	imes block.basefee
]

Thus the maximum gross victim loss from one clone under a fixed base fee is bounded by the resolver reward cap (R), while maximum resolver net from the attack is approximately (R-G) before any priority fee and top-up capital opportunity cost.

## Important boundary

This is an **impact characterization**, not a severity determination.

Whether the observed maker loss constitutes an eligible bounty impact depends on:
- whether the resolver role is an allowed adversary;
- whether resolver reward funding from maker balance is considered an unintended privilege/use of the resolver role;
- whether the same behavior is already disclosed in applicable audits or known issues;
- whether a production-relevant victim state can be reached without relying on artificial assumptions.

No severity or bounty amount is assigned here.
