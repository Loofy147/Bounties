# NativeOrder Resolver Reward / Total-Balance Edge

Snapshot: 2026-09-29
Target: 1inch Limit Order Protocol 4.3.4
Commit: `7da29889efa2e635611e1caf60f85f595ff7f05f`
Status: **OPEN / HYPOTHESIS**

## Observation

`NativeOrderImpl._cancelOrder()` obtains the clone's entire WETH balance, unwraps that full balance, then subtracts the resolver reward from the resulting ETH balance before paying the remainder to the maker.

Therefore an external WETH transfer into a native-order clone can become part of the same balance from which a resolver reward is paid.

## Discriminating experiments

Two local controls are used on `Loofy147/limit-order-protocol`:

- `test/BountyResolverRewardBalance.js`: maker collateral is 1 ETH, a third party adds 1 wei WETH, and a local resolver-access-token holder performs delayed expiry cancellation. Expected accounting:
  - `resolver balance delta + transaction gas = resolverReward`
  - `maker balance delta = 1 ETH + 1 wei - resolverReward`
- `test/BountyResolverUndercollateralizedReward.js`: maker collateral is set below the resolver reward cap (C < R), the resolver adds (R-C) WETH, and delayed expiry cancellation is performed. Expected accounting:
  - maker delta = 0
  - resolver delta + gas = (R)
  - resolver contribution = (R-C)
  - diverted maker collateral = (C)

These are local-flow tests only. They do not, by themselves, claim attacker profitability or bounty eligibility.

## Harness corrections

The resolver cancellation path requires the configured cancellation delay to have elapsed after order expiration when `rewardLimit > 0`.

The initial resolver tests advanced only to expiration. That was a harness defect.

A second harness defect then surfaced in CI: the project does not expose `time.latest` from `require('hardhat')`. Run #28 failed with:

`TypeError: Cannot read properties of undefined (reading 'latest')`

at `test/BountyResolverRewardBalance.js:39`.

No contract assertion failed in that run.

The resolver tests were corrected to derive the latest block timestamp from `ethers.provider.getBlock('latest')` and to advance local time with `evm_increaseTime` + `evm_mine`.

Correction commits:
- `BountyResolverRewardBalance.js` → `1cd6148388902795f2c610ef5ed069feada55528`
- `BountyResolverUndercollateralizedReward.js` → `75f8dfde597a408e28d6e633dad6ea9c805833bc`

## Current execution evidence

Exact-head CI run `36521751170` (run #22) completed successfully on research commit `f0cfc47e1b3593eb01986d8245099f88cbe574e3` and proved the target-pin checks plus the ERC-1271 boundary test (`1 passing`).

Run #28 (`36522855418`) proved:
- boundary test: **PASS**
- isolation test: **PASS**
- resolver reward test: **HARNESS-FAIL**
- undercollateralized test: **SKIPPED**

Current PR head:
`75f8dfde597a408e28d6e633dad6ea9c805833bc`

Current GitHub Actions run:
`36522991905` (run #32)

Latest observed state:
- target pin: **PASS**
- dependency installation: **PASS**
- boundary test: **IN PROGRESS**
- isolation/resolver tests: **PENDING**

Therefore no resolver reproduction result is yet claimed.

## Eligibility question

The current 1inch Immunefi scope excludes attacks requiring privileged addresses and explicitly gives governance and strategist as examples. The page does not name resolver roles.

1inch Fusion documentation describes resolvers as professional market makers and states that the access token gates resolver/settlement participation. The production KycNFT restricts ordinary mint/transfer paths to the contract owner, with owner-signature authorization as an alternate path.

Current classification:
- **ESTABLISHED:** resolver is a permissioned operational actor.
- **INFERENCE / OPEN:** the published bounty text does not explicitly classify resolver/access-token holders as the excluded privileged-address category.

Until that role is resolved, do not promote this hypothesis to `IN-SCOPE`.

## Reopen / promote conditions

Promote only if all are established:

1. The corrected local tests pass against the exact 4.3.4 target.
2. A resolver-access-token holder is within the bounty's adversary model rather than an excluded privileged address.
3. The observed behavior creates an in-scope economic impact under the current program impact table.
4. The behavior is not already disclosed as an unpatched/unresolved audit issue.
5. A minimal victim-impact scenario exists under the permitted local-fork testing model.

Otherwise record the reason and kill the candidate.
