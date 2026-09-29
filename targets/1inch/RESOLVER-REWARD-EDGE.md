# NativeOrder Resolver Reward / Total-Balance Edge

Snapshot: 2026-09-29
Target: 1inch Limit Order Protocol 4.3.4
Commit: `7da29889efa2e635611e1caf60f85f595ff7f05f`
Status: **OPEN / HYPOTHESIS**

## Observation

`NativeOrderImpl._cancelOrder()` obtains the clone's entire WETH balance, unwraps that full balance, then subtracts the resolver reward from the resulting ETH balance before paying the remainder to the maker.

Therefore an external WETH transfer into a native-order clone can become part of the same balance from which a resolver reward is paid.

## Discriminating experiment

`test/BountyResolverRewardBalance.js` on `Loofy147/limit-order-protocol` creates a native order with 1 ETH of maker collateral, adds 1 wei of WETH from a third-party donor, then lets a local resolver-access-token holder cancel after expiry with the maximum calculated reward.

The test's accounting invariants are:

- `resolver balance delta + transaction gas = resolverReward`
- `maker balance delta = 1 ETH + 1 wei - resolverReward`

This is a local-flow test only. It does not claim attacker profitability.

Research artifact commit: `e2f6b9e982e35c0d2fc75b12b3c84f5c6f5fb0c7`

## Eligibility question

The 1inch Immunefi scope excludes attacks requiring privileged addresses, explicitly giving governance and strategist as examples, but the current page does not mention the resolver role by name. The resolver gate in the contract is possession of the production Resolver Access Token.

The production token contract is a KycNFT whose verified source restricts ordinary transfer/mint paths through the contract owner or an owner-signed authorization. This makes resolver acquisition permissioned, but the exact bounty treatment of a resolver-access-token holder is not explicitly resolved by the published scope.

Until that role is classified, this remains **OPEN**, not IN-SCOPE and not a finding.

## Reopen / promote conditions

Promote only if all are established:

1. The local test passes against the exact 4.3.4 target.
2. A resolver-access-token holder is within the bounty's adversary model rather than an excluded privileged address.
3. The behavior creates an in-scope economic impact under the program's impact table.
4. The behavior is not already disclosed as an unpatched/unresolved audit issue.
5. A minimal victim-impact scenario exists without using mainnet/public-testnet deployed code.

Otherwise record the reason and kill the candidate.