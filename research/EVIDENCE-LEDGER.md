# Bounty Evidence Ledger

This ledger prevents loss of work and prevents hypotheses from being mistaken for findings.

| ID | Target | Status | Evidence | Next gate |
|---|---|---|---|---|
| B0-1INCH | 1inch Limit Order Protocol | HYPOTHESIS | Working target `4.3.4` → `7da29889efa2e635611e1caf60f85f595ff7f05f`; public v4.3.4 audit index entry explicitly describes Permit2Proxy; NativeOrderFactory/Impl audit coverage OPEN/UNKNOWN; static review has not established a bypass | execute the new local isolation + ERC-1271 tests; reconcile all applicable audits/known issues; only then assess impact/scope |

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

Negative evidence is preserved:

```text
HYPOTHESIS / REPRODUCED / SUBMITTED
  → REJECTED
```

A rejected candidate is not deleted; the reason is part of the research dataset.

## Current B0 research state

### Current continuation — native-order boundary review (2026-09-29)

### Execution gate — target pin verified

GitHub Actions run `36521745238` is executing the research harness on PR-head commit `f0cfc47e1b3593eb01986d8245099f88cbe574e3`. The target-pin step has now **PASSED** after changing checkout to the exact pull-request head SHA. Dependency installation is in progress; no test assertion result is claimed yet.

This is the first verified execution-stage progress beyond static review.

### Resolver reward total-balance edge (2026-09-29)

### Stronger H-E2 edge — undercollateralized reward (2026-09-29)

The resolver-reward hypothesis was narrowed to a specific condition:

- Let maker collateral be (C).
- Let the current resolver reward cap be (R).
- When (C < R), a resolver can add (R-C) WETH to the clone before expiry cancellation.
- Because the cancellation code pays the reward from the clone's full WETH balance, the resolver then receives (R), while the maker receives (C + (R-C) - R = 0).
- Before gas, the resolver's reward exceeds its own top-up by exactly (C). Thus the additional amount paid by the resolver is effectively converted into the maker's collateral.

This is a **behavioral hypothesis**, not yet a vulnerability or severity claim.

New local control:
- `test/BountyResolverUndercollateralizedReward.js` — commit `26e7265a611aeb2c2ad3a5ec83cf803db7f62a3c`
- workflow includes the control — commit `db8cbdb28f082fc8e31b772c31e41a2082d57c47`

Eligibility remains OPEN. 1inch documents resolver cancellation as a deliberate function requiring a resolver access token and describes resolvers as professional market makers; the published bounty scope excludes some privileged-address attacks but does not name resolvers. This role classification must be settled before any promotion to IN-SCOPE.


A new **OPEN / HYPOTHESIS** was isolated: `NativeOrderImpl._cancelOrder()` pays the resolver reward from the clone's full WETH balance after unwrapping, so third-party WETH donations to a clone become part of the reward source.

Local research control added:
- `test/BountyResolverRewardBalance.js` — corrected test commit `e2f6b9e982e35c0d2fc75b12b3c84f5c6f5fb0c7`
- branch workflow includes boundary, isolation, and resolver-reward controls — commit `8804022fdf1b64b59338e76728d7b816e7e1030e`
- research branch tip observed after these changes: `8804022fdf1b64b59338e76728d7b816e7e1030e`

The test establishes accounting behavior only; it does not establish net attacker profitability or bounty eligibility.

Eligibility remains OPEN because the production resolver access token is permissioned, while the published 1inch scope expressly excludes some privileged-address attacks but does not name the resolver role. The exact role classification must be resolved before promotion.


Static review of the pinned 4.3.4 NativeOrder surface did **not** establish a vulnerability. The main security invariants currently have direct code support:

- Factory binding: `create()` requires `maker == msg.sender`, derives the clone from the original order hash, and patches the effective order maker to the clone.
- ERC-1271 binding: `isValidSignature()` re-derives the clone from the serialized original order, then patches the maker to `address(this)` before comparing the hash.
- Same-maker cross-order isolation is now represented by a dedicated adversarial test.
- Existing upstream tests already cover maker cancellation, resolver cancellation, wrong caller for withdrawal, and partial-fill → cancellation.

New research artifact in the target fork:
- `test/BountyNativeOrderIsolation.js` — commit `9a5ba30d8375006ad337a285b4dab4608fdff1ae`
- research-branch workflow updated to run both NativeOrder boundary suites — commit `94aa51f8a4851cd330e998a9547064ab402e51f7`
- research branch tip after these changes: `94aa51f8a4851cd330e998a9547064ab402e51f7`

Execution remains **UNKNOWN / OPEN** because no GitHub Actions run is currently associated with the branch tip and the local container cannot resolve `github.com`. No passing test result is claimed.


### Audit-coverage gate

The public 1inch audit archive entry for **Limit Order Protocol v4.3.4** describes the audited scope as the **Permit2Proxy extension**. This does not prove that NativeOrderFactory/NativeOrderImpl were never reviewed elsewhere, but there is not yet enough public evidence in this ledger to treat NativeOrder audit coverage as established.

Therefore:

- Permit2Proxy: audit coverage is evidenced by the public archive entry.
- NativeOrderFactory / NativeOrderImpl: audit coverage is **OPEN / UNKNOWN**.
- Any eventual report must compare reproduced behavior against applicable audit/known-issue material before promotion to `IN-SCOPE`.


The canonical hypothesis register is `targets/1inch/HYPOTHESES.md`.

Target pin was refreshed on 2026-09-29 because tag `4.3.4` was created after the earlier `4.3.2` snapshot. `4.3.2` is not treated as the current eligible release.

Tracked families:

- H-A1: mixed partial-fill accounting;
- H-B1: invalidation composition;
- H-C1: authorization/domain equivalence;
- H-D1: dynamic calldata interpretation;
- H-E1: native-order clone / patched-hash equivalence;
- H-E2: native-order collateral / cancellation accounting;
- H-F1: Permit2Proxy authorization boundary.

No one is a confirmed vulnerability.

## Execution-state correction

The prior ledger referenced a hypothesis file that was not present in the current default-branch tree. On 2026-09-29 that inconsistency was corrected by creating the canonical register above.

A local clone/test execution was attempted on 2026-09-29 and again during the current continuation; the agent container had no DNS resolution for `github.com`. Therefore no execution result is claimed from those attempts. GitHub Actions also reported zero runs for the research branch at the time of the last check.

External audit hygiene: Immunefi states that vulnerabilities already disclosed as unpatched or unresolved in completed audits are not eligible for rewards. Audit comparison is therefore a required pre-submission gate.

## Preservation rule

Every significant research step records the exact target version, date, reasoning status, reproduction artifacts and outcome. Do not store credentials or secrets in this repository.
