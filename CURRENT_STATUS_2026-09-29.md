# Bounty Track Current Status — 2026-09-29

**Repository:** `Loofy147/Bounties`

## Current external status

The B0 target remains **1inch Smart Contracts / Limit Order Protocol**.

Current public program evidence checked on 2026-09-29:
- Program is live on Immunefi.
- Maximum bounty: $500,000.
- Proof of concept is required.
- KYC is required for payout.
- The program applies to the latest tags/releases.
- Limit Order Protocol remains an in-scope asset.

The 1inch repository target is tag `4.3.4`, underlying commit `7da29889efa2e635611e1caf60f85f595ff7f05f`. `4.3.2` is retained only as historical baseline context.

## Execution gate — 2026-09-29

Exact-head CI run `36521751170` (run #22) completed **SUCCESS** on research commit `f0cfc47e1b3593eb01986d8245099f88cbe574e3`.

That run established:
- exact target checkout and 4.3.4 package-version verification;
- `test/BountyNativeOrderBoundary.js`: **1 passing**.

It did not run the remaining isolation/resolver controls because the workflow at that commit contained only the boundary test.

The workflow was then expanded in commit `c455fe9ae5938b05163c58010052a03b8afa7d1d` to run four independent controls:
1. `BountyNativeOrderBoundary.js`
2. `BountyNativeOrderIsolation.js`
3. `BountyResolverRewardBalance.js`
4. `BountyResolverUndercollateralizedReward.js`

Run #28 (`36522855418`) established:
- target pin: **PASS**;
- boundary test: **PASS**;
- isolation test: **PASS**;
- resolver reward test: **FAIL** with `TypeError: Cannot read properties of undefined (reading 'latest')` at `test/BountyResolverRewardBalance.js:39`;
- undercollateralized test: **SKIPPED** because the previous step failed.

This was classified as a **test-harness defect**, not a contract result.

The resolver tests were then corrected to use the project's provider RPC controls (`evm_increaseTime` + `evm_mine`) and to advance beyond the configured resolver cancellation delay:
- `BountyResolverRewardBalance.js` → `1cd6148388902795f2c610ef5ed069feada55528`
- `BountyResolverUndercollateralizedReward.js` → `75f8dfde597a408e28d6e633dad6ea9c805833bc`

Current research branch / PR head:
`75f8dfde597a408e28d6e633dad6ea9c805833bc`

Current GitHub Actions run #32 (`36522991905`) is executing the corrected matrix. Latest observed state:
- target pin: **PASS**;
- dependency installation: **PASS**;
- `BountyNativeOrderBoundary.js`: **IN PROGRESS**;
- remaining three tests: **PENDING**.

## Resolver adversary-model gate

The current public Immunefi scope names Limit Order Protocol as in scope, lists direct theft of user funds as an in-scope Critical impact, and says the program applies to latest tags/releases. Its privileged-address exclusion explicitly names governance and strategist, but does not name resolver/access-token-holder roles.

1inch Fusion documentation describes resolvers as professional market makers and the KYC/access token as the mechanism gating resolver participation.

Current classification:
- **ESTABLISHED:** resolver is a permissioned operational actor.
- **INFERENCE / OPEN:** the published bounty language does not explicitly classify resolver/access-token holders as the excluded privileged-address category.

This is not an `IN-SCOPE` determination. Economic impact, adversary eligibility, and audit/known-issue reconciliation remain separate gates.

## NativeOrder economic hypothesis — H-E2

Static review + local harness design isolate the following condition:

When maker collateral (C) is below resolver reward cap (R), an external WETH transfer of (R-C) can make the clone balance exactly (R). The cancellation path then pays (R) from the clone balance to the resolver, leaving zero from that cancellation balance for the maker.

This remains a **behavioral hypothesis**, not a confirmed vulnerability, profitability claim, severity, or eligibility determination.

The local tests use a mock access token solely to construct a controlled resolver-like execution environment; this is not evidence that an arbitrary external account can obtain the production resolver role.

## Audit coverage correction

The current public audit evidence used here identifies the v4.3.4 audit entry with the **Permit2Proxy extension**. NativeOrderFactory and NativeOrderImpl are present in the 4.3.4 code, but current evidence is insufficient to mark their audit coverage as established.

NativeOrder audit/known-issue reconciliation remains mandatory before any submission decision.

## Local research status

Status remains:

`HYPOTHESIS`

No vulnerability has been established.

Current target:
- tag: `4.3.4`
- commit: `7da29889efa2e635611e1caf60f85f595ff7f05f`
- tag object: `0a40e01befff19d925457b55191900fb456c2dd2`

Current execution frontier:

`target pin PASS → boundary PASS → isolation PASS → corrected resolver matrix RUNNING`

## Re-verification gate

Before any submission:
1. re-pin current Immunefi scope;
2. verify exact eligible release/tag;
3. verify in-scope asset;
4. verify impact mapping;
5. reconcile audits and known issues;
6. verify permitted test environment and techniques;
7. preserve the exact reproduction evidence and reporting timeline.

Testing remains local-only; the public program prohibits testing mainnet/public-testnet deployed code.

## Commercial role

The success metric is:

`RECONNAISSANCE → REPRODUCED → IN-SCOPE → SUBMITTED → ACCEPTED → PAID`

The first monetary milestone is one legitimate paid finding.

## Separation rule

- `Bounties`: external security research.
- `client-proof`: commercial engineering evidence.
- `proposals`: acquisition and sales control plane.
- `Open-System-One`: research laboratory.

Security research findings are never represented as client engineering experience unless independently applicable and accurately described.


## Latest verified execution — run #32

Run `36522991905` (run #32) completed **SUCCESS** on research commit `75f8dfde597a408e28d6e633dad6ea9c805833bc`.

All four research controls passed:
- NativeOrder ERC-1271 boundary: **1 passing**
- NativeOrder clone isolation: **1 passing**
- resolver reward total-balance control: **1 passing**
- undercollateralized resolver reward control: **1 passing**

Therefore the local behavior behind H-E2 is now **EXPERIMENTALLY_SUPPORTED**.

The test uses a mock resolver access token and a local Hardhat deployment. It does not establish that an arbitrary external account can obtain the production resolver role, nor that the behavior is bounty-eligible.

The next gates are now:
`resolver adversary eligibility → audit/known-issue reconciliation → minimal victim-impact characterization → submission eligibility`

No severity or bounty amount is assigned yet.