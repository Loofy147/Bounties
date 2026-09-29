
# Bounty Evidence Ledger

This ledger prevents loss of work and prevents hypotheses from being mistaken for findings.

| ID | Target | Status | Evidence | Next gate |
|---|---|---|---|---|
| B0-1INCH | 1inch Limit Order Protocol | HYPOTHESIS | Target 4.3.4 pinned; H-E2 and the natural partial-fill residual path are EXPERIMENTALLY_SUPPORTED; run #64 completed all six controls; victim loss 0.0007 ETH, resolver net -0.00006743195654982 ETH | reconcile audits/known issues; settle resolver-role treatment; establish production deployment/version correspondence and minimum real victim state |

## Evidence stages

RECONNAISSANCE
  -> HYPOTHESIS
  -> REPRODUCED
  -> IN-SCOPE
  -> SUBMITTED
  -> ACCEPTED
  -> PAID

Rejected candidates remain recorded with the reason.

## Current B0 frontier — 2026-09-29

### Target

- Tag: 4.3.4
- Commit: 7da29889efa2e635611e1caf60f85f595ff7f05f
- Tag object: 0a40e01befff19d925457b55191900fb456c2dd2

### Full corrected reproduction

Run #32 (36522991905) on research commit 75f8dfde597a408e28d6e633dad6ea9c805833bc completed SUCCESS.

Four controls passed:
- BountyNativeOrderBoundary.js
- BountyNativeOrderIsolation.js
- BountyResolverRewardBalance.js
- BountyResolverUndercollateralizedReward.js

Execution evidence state:
- target pin: EXPERIMENTALLY_SUPPORTED
- ERC-1271 boundary: EXPERIMENTALLY_SUPPORTED
- same-maker cross-order isolation: EXPERIMENTALLY_SUPPORTED
- resolver total-balance behavior: EXPERIMENTALLY_SUPPORTED
- undercollateralized resolver reward: EXPERIMENTALLY_SUPPORTED

### H-E2 reproduced condition

At a local base fee of 10 gwei:
- maker residual C = 0.0001 ETH in the initial undercollateralized reproduction;
- resolver reward cap R = 0.00077 ETH;
- resolver top-up T = R-C = 0.00067 ETH.

After expiry plus the configured delay, the resolver cancellation path transfers the full reward from the aggregate clone balance. The maker receives zero cancellation proceeds in that constructed state.

This is a reproduced local behavior, not yet an eligible finding.

### Victim-loss calibration

A dedicated calibration control succeeded in GitHub Actions run #51 (36524919906), job 109265719467, on head e39993268632cc0b758ec7be98cd31048699949c.

Observed:
- maker residual C = 0.0007 ETH
- reward cap R = 0.00077 ETH
- resolver top-up T = 0.00007 ETH
- cancellation gas used = 56,627
- effective gas price = 11 gwei
- cancellation gas cost = 0.000622897 ETH
- victim cancellation loss = 0.0007 ETH
- resolver reward = 0.00077 ETH

The calibration intentionally isolates victim loss from resolver profitability.

### Natural victim-state evidence

The upstream 4.3.4 test suite includes a native ETH-maker-order partial-fill case in which a 0.3 ETH-equivalent native order is filled for 0.2 and the clone retains 0.1 WETH. A subsequent maker cancellation refunds that residual.

Run #64 additionally reproduced a natural residual of 0.0007 ETH, then completed resolver cancellation with the reward cap at 0.00077 ETH.

Therefore residual clone collateral after partial fill is a normal protocol state.

A dedicated bounty control targets the same transition with a residual C below the resolver reward cap and complete resolver-side accounting.

### Harness history

Run #28 (36522855418) failed only because time.latest was unavailable through require('hardhat'). The contract itself did not fail an assertion.

Later fixes used ethers.provider.getBlock('latest') plus evm_increaseTime/evm_mine and produced run #32 SUCCESS.

The new partial-fill control initially had a second HARNESS_DEFECT: makerTraits was encoded as {} instead of constructing the order with buildOrder(baseOrder, {}), causing an ethers v6 invalid BigNumberish error.

That defect was corrected in commit:
add07cf4859a7128393129f1e72ccdc8bfd77c60

A new PR run for that head was initiated after reopening the draft PR; the last observed run was still in progress.

### Resolver adversary model

ESTABLISHED:
resolver is a permissioned operational actor and the intended caller of resolver cancellation.

OPEN / INFERENCE:
the current bounty language excludes attacks requiring privileged addresses and names governance and strategist as examples, but does not expressly classify resolver/access-token-holder roles.

Therefore technical reachability by the resolver role does not by itself establish bounty eligibility.

### Design-intent / known-issue investigation

Upstream PR #390 explicitly discussed whether the whole WETH balance should be returned to the maker, including accidentally deposited WETH. The maintainer stated that this full-balance behavior was intentional.

This establishes conscious full-balance semantics, not that the undercollateralized reward interaction was previously recognized.

Targeted GitHub issue/PR/source searches found no explicit prior disclosure of the tested undercollateralized resolver-reward condition.

Absence is not novelty proof.

### Audit gate

The official 1inch audit archive contains a v4.3.4 OpenZeppelin report entry. Current archive evidence associates that entry with the Permit2Proxy extension.

This does not establish coverage of NativeOrderFactory/NativeOrderImpl by that particular report, and does not prove that NativeOrder was never audited elsewhere.

Applicable audit and known-issue reconciliation remains OPEN.

## Economic interpretation

The completed natural partial-fill run measured resolverNetTotal = -0.00006743195654982 ETH against victimResidualLoss = 0.0007 ETH. This is negative-EV for the measured local scenario, but it is not used as an impact-kill gate; current Immunefi guidance treats attacker financial risk/ROI as a feasibility consideration rather than an automatic invalidation of the underlying impact.


For C<R and T=R-C:

- total clone balance becomes R;
- resolver reward is R;
- maker receives zero cancellation proceeds;
- maker loss attributable to the reward path is C.

Thus the mechanism can consume 100% of the maker's residual clone collateral in the tested model.

Do not use the earlier shorthand C > cancellation-gas as a full profitability condition. Complete resolver economics must include top-up cost and the gas to acquire and transfer the top-up.

### Research endpoint

No further contract-level variant is currently justified on the existing evidence. H-E2/K-04 has a complete local reproduction from normal partial-fill state through resolver cancellation and complete cost accounting. The remaining gates are external to that reproduction: applicable audit/known-issue disclosure, resolver-role eligibility interpretation, and production prevalence/minimum victim-state evidence.

## Current decision state

B0-1INCH overall: HYPOTHESIS

H-E2 local behavior: EXPERIMENTALLY_SUPPORTED

Bounty eligibility: OPEN

No severity, bounty amount, or submission decision has been assigned.

## Preservation rule

Record exact version, ref/commit, execution result, status transition, and next discriminating action for every material step. Never store credentials or secrets.
