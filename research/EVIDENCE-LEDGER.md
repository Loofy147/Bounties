# Bounty Evidence Ledger

This ledger prevents loss of work and prevents hypotheses from being mistaken for findings.

| ID | Target | Status | Evidence | Next gate |
|---|---|---|---|---|
| B0-1INCH | 1inch Limit Order Protocol | HYPOTHESIS | Target 4.3.4 pinned; H-E2 resolver-reward edge is EXPERIMENTALLY_SUPPORTED locally; bounty eligibility and audit/known-issue reconciliation remain OPEN | settle resolver adversary eligibility; reconcile audits/known issues; characterize minimum victim impact |

## Evidence stages

```text
RECONNAISSANCE
  → HYPOTHESIS
  → REPRODUCED
  → IN-SCOPE
  → SUBMITTED
  → ACCEPTED
  → PAID
```

Rejected candidates remain recorded with the reason.

## Current B0 frontier — 2026-09-29

### Target

- Tag: `4.3.4`
- Commit: `7da29889efa2e635611e1caf60f85f595ff7f05f`
- Tag object: `0a40e01befff19d925457b55191900fb456c2dd2`

### Execution

Exact-head run #22 (`36521751170`) established:
- target pin PASS;
- package version 4.3.4 PASS;
- NativeOrder ERC-1271 boundary: 1 passing.

The expanded four-control run #28 (`36522855418`) established:
- boundary: PASS;
- same-maker clone isolation: PASS;
- resolver test: HARNESS-FAIL;
- undercollateralized resolver test: skipped.

Run #28 failed at `time.latest` being unavailable through `require('hardhat')`. No contract assertion failed.

The resolver harness was corrected using `ethers.provider.getBlock('latest')` and `evm_increaseTime`/`evm_mine`.

### Full corrected reproduction

Run #32 (`36522991905`) on research commit `75f8dfde597a408e28d6e633dad6ea9c805833bc` completed **SUCCESS**.

All four controls passed:
- `BountyNativeOrderBoundary.js`: 1 passing
- `BountyNativeOrderIsolation.js`: 1 passing
- `BountyResolverRewardBalance.js`: 1 passing
- `BountyResolverUndercollateralizedReward.js`: 1 passing

Execution evidence state:
- target pin: **EXPERIMENTALLY_SUPPORTED**
- ERC-1271 boundary: **EXPERIMENTALLY_SUPPORTED**
- same-maker cross-order isolation: **EXPERIMENTALLY_SUPPORTED**
- resolver total-balance behavior: **EXPERIMENTALLY_SUPPORTED**
- undercollateralized resolver reward: **EXPERIMENTALLY_SUPPORTED**

### H-E2 reproduced condition

At a local base fee of 10 gwei:
- maker collateral (C = 0.0001) ETH;
- resolver reward cap (R = 0.00077) ETH;
- resolver top-up (R-C = 0.00067) ETH.

After expiry plus the configured cancellation delay, the resolver cancellation path transfers the full reward from the clone balance. The test observes zero maker balance delta from the cancellation and resolver proceeds equal to (R) after adding gas cost back.

This is a reproduced local behavior, not yet an eligible finding.

### Resolver adversary model

**ESTABLISHED:** resolver is a permissioned operational actor and the intended caller of resolver cancellation.

**OPEN / INFERENCE:** the published 1inch bounty language does not explicitly state whether resolver/access-token holders are excluded by the privileged-address rule. The scope gives governance and strategist as its named examples. The role therefore cannot be auto-promoted to IN-SCOPE solely from its operational nature. citeturn314897view0

1inch's current resolver material states that resolvers must register/pass verification and that an Access NFT functions as an access credential for exclusive order-fulfillment functionality. citeturn595204search5turn595204search8

### Design-intent / known-issue investigation

Upstream `1inch/limit-order-protocol` PR #390 explicitly discussed whether the **whole WETH balance** should be returned to the maker, including accidentally deposited WETH. The maintainer stated that this was intended, while the same implementation subtracts resolver reward from the clone's full balance before paying the maker.

This is evidence of a consciously designed full-balance semantic, not proof that H-E2 was recognized.

Current search over the upstream code/PR material found no explicit prior disclosure using the tested formulation (resolver reward funded by an undercollateralized clone balance via external WETH top-up). That absence is not proof of novelty.

### Audit gate

The official 1inch audit archive contains a v4.3.4 OpenZeppelin report file. citeturn812425view0

The archive material currently available in this research describes the v4.3.4 entry as the Permit2Proxy extension; therefore the present evidence does not establish NativeOrderFactory/NativeOrderImpl coverage by that particular v4.3.4 audit.

Do not infer “never audited.” Earlier Limit Order / Fusion audits cover other code snapshots and components. Applicable audit and known-issue reconciliation remains OPEN.

## Current decision state

B0-1INCH overall: **HYPOTHESIS**

H-E2 local behavior: **EXPERIMENTALLY_SUPPORTED**

Bounty eligibility: **OPEN**

No severity, bounty amount, or submission decision has been assigned.

## Preservation rule

Record exact version, ref/commit, execution result, status transition, and next discriminating action for every material step. Never store credentials or secrets.


## Economic impact characterization — 2026-09-29

The reproduced H-E2 behavior can be expressed exactly for a clone containing only maker collateral (C) plus resolver top-up (T):

[
R=min(rewardLimit,;block.basefee	imes70,000	imes1.1)
]

For (C<R), selecting (T=R-C) makes the clone balance equal (R), so maker proceeds from cancellation are zero.

Therefore:
[
	ext{maker loss}=C
]
[
	ext{resolver net after top-up and gas}=C-G
]

At 10 gwei, using the 56,603-gas figure observed in run #32:
[
R=0.00077	ext{ ETH},quad Gapprox0.00056603	ext{ ETH}
]

The original (C=0.0001) ETH reproduction is therefore behaviorally valid but economically loss-making for the resolver at that fee. Break-even is approximately (C>G). A calibration test with (C=0.0007) ETH was added to the target branch to verify the profitable edge under the same local assumptions.

Calibration artifact:
`Loofy147/limit-order-protocol:test/BountyResolverRewardEconomicCalibration.js`

Calibration branch commit:
`64b213a198891854e8b74f5f8fdb530895f48411`

Workflow extension:
`41d0c3b434233c68d7d38726094e093c2f320e6e`

Current calibration CI: run #38 (`36523930512`), assertion result **PENDING**.

This is impact characterization, not severity classification or bounty-eligibility determination.
