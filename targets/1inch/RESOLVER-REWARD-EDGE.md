# NativeOrder Resolver Reward / Total-Balance Edge

Snapshot: 2026-09-29
Target: 1inch Limit Order Protocol 4.3.4
Commit: `7da29889efa2e635611e1caf60f85f595ff7f05f`
Status: **EXPERIMENTALLY_SUPPORTED / ELIGIBILITY OPEN**

## Observation

`NativeOrderImpl._cancelOrder()` reads the clone's **entire WETH balance**, unwraps it, then subtracts the resolver reward before paying the remainder to the maker.

Thus, any WETH already resident in the clone is part of the balance from which the resolver reward is funded.

## Reproduced control

Two local controls were executed against the 4.3.4 target:

- `BountyResolverRewardBalance.js`: maker collateral 1 ETH plus a 1-wei third-party WETH donation; resolver cancellation receives the configured reward from the aggregate clone balance.
- `BountyResolverUndercollateralizedReward.js`: maker collateral (C) is below the resolver reward cap (R); the resolver supplies (R-C) WETH, then performs delayed expiry cancellation.

Run #32:
- GitHub Actions run `36522991905`
- research commit `75f8dfde597a408e28d6e633dad6ea9c805833bc`
- result: **SUCCESS**
- boundary: 1 passing
- clone isolation: 1 passing
- resolver reward balance: 1 passing
- undercollateralized resolver reward: 1 passing

For the undercollateralized control:
- (C = 0.0001) ETH
- (R = 0.00077) ETH at a 10 gwei base fee
- resolver top-up (R-C = 0.00067) ETH

The test asserts:
- maker cancellation-related balance delta = 0
- resolver balance delta + gas cost = (R)
- resolver contribution = (R-C)

Therefore the local execution isolates (C) ETH of maker collateral as the amount recovered by the resolver beyond its own top-up, before gas accounting.

## Harness history

The first resolver harness had two defects:
1. cancellation-delay timing was omitted;
2. the project did not expose `time.latest` through `require('hardhat')`.

Run #28 `36522855418` failed only on the second harness issue:
`TypeError: Cannot read properties of undefined (reading 'latest')`.

The contract was not changed. The tests were corrected to use the provider timestamp and local EVM time controls:
- `BountyResolverRewardBalance.js` → `1cd6148388902795f2c610ef5ed069feada55528`
- `BountyResolverUndercollateralizedReward.js` → `75f8dfde597a408e28d6e633dad6ea9c805833bc`

## Design-intent evidence

Upstream `1inch/limit-order-protocol` PR #390 contains an explicit review exchange about full-balance recovery.

A reviewer asked whether the implementation should send the **whole WETH balance** to the maker, including accidentally deposited WETH. The maintainer answered that this is intentional because WETH remaining after cross-chain cancellation is treated as accidentally deposited and should be returned to the maker; the maker also has `withdraw` available.

The same PR's implementation places resolver reward subtraction after reading the clone's full WETH balance.

This is not proof that the current H-E2 behavior was overlooked, but it establishes that full-balance semantics were a consciously discussed design property.

## Eligibility / adversary model

1inch's public bounty scope:
- includes Limit Order Protocol;
- applies to latest tags/releases;
- includes direct theft of user funds as a Critical impact;
- excludes attacks requiring privileged addresses, with governance and strategist given as examples. citeturn314897view0

Current 1inch resolver materials describe resolvers as verified/registered professional actors and state that an Access NFT is issued as an access credential for exclusive order-fulfillment functionality. citeturn595204search5turn595204search8

Classification:
- **ESTABLISHED:** resolver is a permissioned operational actor and is the intended caller of the resolver-cancellation function.
- **OPEN / INFERENCE:** the published 1inch bounty text does not explicitly state whether resolver/access-token holders fall inside or outside the privileged-address exclusion.

Do not treat the current resolver eligibility as established merely because the role is operational rather than governance.

## Audit / known-issue gate

The official 1inch audit archive currently contains a v4.3.4 OpenZeppelin report file. citeturn812425view0

The archive README used in this research describes the v4.3.4 entry specifically as the Permit2Proxy extension; current evidence therefore does not establish that NativeOrderFactory/NativeOrderImpl were covered by that v4.3.4 audit. This is an evidence gap, not evidence that they were never reviewed elsewhere.

The next gate is explicit reconciliation against:
- the v4.3.4 audit material;
- earlier NativeOrder/ETH-order reviews and PR discussions;
- any known/disclosed issue concerning resolver reward funding from aggregate clone balance.

## Promotion conditions

Promote beyond `EXPERIMENTALLY_SUPPORTED / ELIGIBILITY OPEN` only when all are established:

1. Resolver/access-token-holder is an accepted adversary under the current bounty rules.
2. The reproduced behavior maps to an in-scope user-fund impact.
3. No applicable audit/known issue already discloses the same behavior.
4. A minimal victim scenario is established under the permitted local-fork model.

Until then: **do not submit** and do not assign a severity or bounty amount.
