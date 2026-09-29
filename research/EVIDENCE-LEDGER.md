# Bounty Evidence Ledger

This ledger prevents loss of work and prevents hypotheses from being mistaken for findings.

| ID | Target | Status | Evidence | Next gate |
|---|---|---|---|---|
| B0-1INCH | 1inch Limit Order Protocol | HYPOTHESIS | Working target `4.3.4` → `7da29889efa2e635611e1caf60f85f595ff7f05f`; public v4.3.4 audit index entry explicitly describes Permit2Proxy; NativeOrderFactory/Impl audit coverage OPEN/UNKNOWN; static review has not established a bypass | complete the full local boundary/reward matrix in CI; reconcile all applicable audits/known issues; only then assess impact/scope |

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

### Execution re-verification — 2026-09-29

The first exact-head CI run, `36521751170` (run #22), completed **SUCCESS** on PR-head commit `f0cfc47e1b3593eb01986d8245099f88cbe574e3`.

What it actually established:
- target pin verification **PASS**;
- package version check **PASS** for 4.3.4;
- `test/BountyNativeOrderBoundary.js`: **1 passing**;
- the successful run did **not** execute the isolation or resolver-reward tests because the workflow still contained only the boundary test at that commit.

The research workflow was then expanded on branch `bounty/research-4.3.4` to execute four separate controls:
1. `BountyNativeOrderBoundary.js`
2. `BountyNativeOrderIsolation.js`
3. `BountyResolverRewardBalance.js`
4. `BountyResolverUndercollateralizedReward.js`

Workflow expansion commit: `c455fe9ae5938b05163c58010052a03b8afa7d1d`.

During review of the new resolver controls, a test-harness timing defect was found: `NativeOrderImpl.cancelExpiredOrderByResolver()` requires the configured cancellation delay to have elapsed after expiration. Both resolver tests had advanced only to `expiration`. This was a **harness defect, not a contract result**.

Harness correction commits:
- `test/BountyResolverRewardBalance.js`: `0f684b3191636d2677d6028e61b14182ec638476`
- `test/BountyResolverUndercollateralizedReward.js`: `6fd8f86fc4476ec70d110a62b275bf7b85d19429`

The resulting PR head is `6fd8f86fc4476ec70d110a62b275bf7b85d19429`.

GitHub Actions run #28 (`36522855418`) is now executing that corrected four-control matrix. At the latest observation:
- target pin verification **PASS**;
- dependency installation **IN PROGRESS**;
- all four test assertion steps still **PENDING**.

Therefore the full resolver experiment remains **UNKNOWN / OPEN** until run #28 produces assertion results.

### Resolver adversary-model gate — 2026-09-29

Current public 1inch bounty scope:
- Limit Order Protocol is an in-scope asset.
- The program applies only to latest tags/releases.
- Direct theft of user funds is an in-scope Critical impact.
- The privileged-address exclusion explicitly names governance and strategist, but does not name resolver/access-token-holder roles.

Current 1inch Fusion repository material describes resolvers as professional market makers, with the access token used to gate resolver/settlement participation. `KycNFT` mint/ordinary transfer paths are owner-controlled or owner-signature-authorized. Therefore:

**Established:** resolver is a permissioned operational role.

**Inference / OPEN:** the published bounty text does not explicitly classify that role as an excluded privileged address.

This does not yet promote H-E2 to `IN-SCOPE`; economic impact, exact adversary eligibility, and audit/known-issue reconciliation remain separate gates.

### Resolver reward total-balance edge (2026-09-29)

### Stronger H-E2 edge — undercollateralized reward (2026-09-29)

The resolver-reward hypothesis was narrowed to a specific condition:

- Let maker collateral be (C).
- Let the current resolver reward cap be (R).
- When (C < R), a resolver can add (R-C) WETH to the clone before expiry cancellation.
- Because the cancellation code pays the reward from the clone's full WETH balance, the resolver then receives (R), while the maker receives (C + (R-C) - R = 0).
- Before gas, the resolver's reward exceeds its own top-up by exactly (C). Thus the additional amount paid by the resolver is effectively converted into the maker's collateral.

This is a **behavioral hypothesis**, not yet a vulnerability or severity claim.

The discriminating local control is now corrected to honor the configured cancellation delay:
- `test/BountyResolverUndercollateralizedReward.js` — latest commit `6fd8f86fc4476ec70d110a62b275bf7b85d19429`
- four-control workflow — latest branch head `6fd8f86fc4476ec70d110a62b275bf7b85d19429`

Eligibility remains OPEN.

### NativeOrder boundary review

Static review of the pinned 4.3.4 NativeOrder surface did **not** establish a vulnerability. The main security invariants currently have direct code support:

- Factory binding: `create()` requires `maker == msg.sender`, derives the clone from the original order hash, and patches the effective order maker to the clone.
- ERC-1271 binding: `isValidSignature()` re-derives the clone from the serialized original order, then patches the maker to `address(this)` before comparing the hash.
- Same-maker cross-order isolation is represented by a dedicated adversarial test.
- Existing upstream tests cover maker cancellation, resolver cancellation, wrong caller for withdrawal, and partial-fill → cancellation.

The exact-head boundary test is now **EXPERIMENTALLY_SUPPORTED** by run #22 (1 passing). The additional isolation and resolver tests remain **UNKNOWN / OPEN** pending run #28.

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

## Preservation rule

Every significant research step records the exact target version, date, reasoning status, reproduction artifacts and outcome. Do not store credentials or secrets in this repository.
