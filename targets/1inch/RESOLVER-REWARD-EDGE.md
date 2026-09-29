# NativeOrder Resolver Reward / Total-Balance Edge

Snapshot: 2026-09-29
Target: 1inch Limit Order Protocol 4.3.4
Commit: `7da29889efa2e635611e1caf60f85f595ff7f05f`
Status: **OPEN / HYPOTHESIS**

## Observation

`NativeOrderImpl._cancelOrder()` obtains the clone's entire WETH balance, unwraps that full balance, then subtracts the resolver reward from the resulting ETH balance before paying the remainder to the maker.

Therefore an external WETH transfer into a native-order clone can become part of the same balance from which a resolver reward is paid.

## Discriminating experiment

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

### Harness correction

The resolver cancellation path requires the configured cancellation delay to have elapsed after order expiration when `rewardLimit > 0`.

The initial resolver tests advanced only to `expiration`; this was a test-harness defect. The contract was not changed.

Correction commits:
- `BountyResolverRewardBalance.js` → `0f684b3191636d2677d6028e61b14182ec638476`
- `BountyResolverUndercollateralizedReward.js` → `6fd8f86fc4476ec70d110a62b275bf7b85d19429`

## Current execution evidence

Exact-head CI run `36521751170` (run #22) completed successfully on research commit `f0cfc47e1b3593eb01986d8245099f88cbe574e3` and proved the target-pin checks plus the ERC-1271 boundary test (`1 passing`).

That run did not execute the resolver controls.

The branch workflow was expanded to four independent test steps in commit `c455fe9ae5938b05163c58010052a03b8afa7d1d`.

Current PR head:
`6fd8f86fc4476ec70d110a62b275bf7b85d19429`

Current GitHub Actions run:
`36522855418` (run #28)

Latest observed state:
- target pin: **PASS**
- dependency installation: **IN PROGRESS**
- boundary/isolation/reward/undercollateralized assertion steps: **PENDING**

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
