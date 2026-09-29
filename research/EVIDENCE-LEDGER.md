# Bounty Evidence Ledger

This ledger prevents loss of work and prevents hypotheses from being mistaken for findings.

| ID | Target | Status | Evidence | Next gate |
|---|---|---|---|---|
| B0-1INCH | 1inch Limit Order Protocol | HYPOTHESIS | Working target `4.3.4` → `7da29889efa2e635611e1caf60f85f595ff7f05f`; public v4.3.4 audit index entry explicitly describes Permit2Proxy; NativeOrderFactory/Impl audit coverage OPEN/UNKNOWN; static review has not established a bypass | complete corrected boundary/isolation/reward matrix in CI; reconcile all applicable audits/known issues; only then assess impact/scope |

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
- the successful run did **not** execute the isolation or resolver-reward tests because the workflow at that commit still contained only the boundary test.

The workflow was then expanded in commit `c455fe9ae5938b05163c58010052a03b8afa7d1d` to execute four separate controls:
1. `BountyNativeOrderBoundary.js`
2. `BountyNativeOrderIsolation.js`
3. `BountyResolverRewardBalance.js`
4. `BountyResolverUndercollateralizedReward.js`

Run #28 (`36522855418`) then established:
- target pin **PASS**;
- boundary test **PASS**;
- isolation test **PASS**;
- resolver reward test **FAIL**, but the failure was entirely in the test harness: `TypeError: Cannot read properties of undefined (reading 'latest')` at `test/BountyResolverRewardBalance.js:39`;
- undercollateralized test was skipped because the previous step failed.

This failure is classified as **HARNESS_DEFECT**, not a contract result.

The resolver tests were corrected to use the project's available provider RPC time controls (`evm_increaseTime` + `evm_mine`) and to advance past the configured cancellation delay:
- `test/BountyResolverRewardBalance.js` → `1cd6148388902795f2c610ef5ed069feada55528`
- `test/BountyResolverUndercollateralizedReward.js` → `75f8dfde597a408e28d6e633dad6ea9c805833bc`

Current research branch / PR head:
`75f8dfde597a408e28d6e633dad6ea9c805833bc`

GitHub Actions run #32 (`36522991905`) is executing the corrected four-control matrix. Latest observed state:
- target-pin verification **PASS**;
- dependency installation **PASS**;
- `BountyNativeOrderBoundary.js`: **IN PROGRESS**;
- remaining three assertion steps: **PENDING**.

Therefore the resolver reproduction remains **UNKNOWN / OPEN**.

### Resolver adversary-model gate — 2026-09-29

Current public 1inch bounty scope:
- Limit Order Protocol is an in-scope asset.
- The program applies to latest tags/releases.
- Direct theft of user funds is an in-scope Critical impact.
- The privileged-address exclusion explicitly names governance and strategist, but does not name resolver/access-token-holder roles.

Current 1inch Fusion repository material describes resolvers as professional market makers, with the access token used to gate resolver/settlement participation. `KycNFT` mint/ordinary transfer paths are owner-controlled or owner-signature-authorized.

**Established:** resolver is a permissioned operational role.

**Inference / OPEN:** the published bounty language does not explicitly classify resolver/access-token holders as the excluded privileged-address category.

This does not promote H-E2 to `IN-SCOPE`; economic impact, exact adversary eligibility, and audit/known-issue reconciliation remain separate gates.

### Stronger H-E2 edge — undercollateralized reward

The resolver-reward hypothesis is narrowed to:

- maker collateral = (C);
- resolver reward cap = (R);
- when (C < R), an external WETH transfer of (R-C) can make the clone balance exactly (R);
- `_cancelOrder()` then pays (R) from the clone balance to the resolver, leaving zero from that cancellation balance for the maker;
- before gas, the resolver receives exactly its top-up plus (C).

This remains a **behavioral hypothesis**, not a confirmed vulnerability, severity, profitability claim, or eligibility determination.

### NativeOrder boundary review

Static review of the pinned 4.3.4 NativeOrder surface did **not** establish a vulnerability.

The exact-head boundary test is **EXPERIMENTALLY_SUPPORTED** by run #22 (1 passing).

The same-maker cross-order isolation test is also **EXPERIMENTALLY_SUPPORTED** by run #28.

The resolver reward controls remain **UNKNOWN / OPEN** pending the corrected run #32.

### Audit-coverage gate

The public 1inch audit archive entry currently used in this research describes the v4.3.4 audit entry as the **Permit2Proxy extension**. This does not prove NativeOrderFactory/NativeOrderImpl were never reviewed elsewhere.

Therefore:
- Permit2Proxy: audit coverage evidenced.
- NativeOrderFactory / NativeOrderImpl: audit coverage **OPEN / UNKNOWN**.
- Any eventual report must reconcile reproduced behavior against applicable audit/known-issue material before promotion to `IN-SCOPE`.

The canonical hypothesis register is `targets/1inch/HYPOTHESES.md`.

Target pin:
- tag `4.3.4`
- commit `7da29889efa2e635611e1caf60f85f595ff7f05f`
- tag object `0a40e01befff19d925457b55191900fb456c2dd2`

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


## Latest verified execution — run #32 (2026-09-29)

GitHub Actions run `36522991905` (run #32) completed **SUCCESS** on research commit `75f8dfde597a408e28d6e633dad6ea9c805833bc`.

All four controls passed independently:
- `BountyNativeOrderBoundary.js`: **1 passing**
- `BountyNativeOrderIsolation.js`: **1 passing**
- `BountyResolverRewardBalance.js`: **1 passing**
- `BountyResolverUndercollateralizedReward.js`: **1 passing**

This upgrades the execution state as follows:
- target pin: **EXPERIMENTALLY_SUPPORTED**
- NativeOrder ERC-1271 boundary: **EXPERIMENTALLY_SUPPORTED**
- same-maker cross-order isolation: **EXPERIMENTALLY_SUPPORTED**
- resolver total-balance behavior: **EXPERIMENTALLY_SUPPORTED**
- undercollateralized reward behavior: **EXPERIMENTALLY_SUPPORTED**

The four tests run against the pinned 4.3.4 code line. This establishes the observed local behavior. It does **not** by itself establish bounty eligibility, severity, real-production liquidity exposure, or absence from prior disclosures/audits.

For the undercollateralized case, the test constructs (C=0.0001) ETH maker collateral and (R=0.00077) ETH resolver reward cap at a 10 gwei base fee, then supplies (R-C=0.00067) ETH of WETH before delayed resolver cancellation. The assertions show zero maker balance delta from the cancellation and resolver proceeds equal to (R) after adding gas cost back. This is the key reproduced H-E2 behavior.