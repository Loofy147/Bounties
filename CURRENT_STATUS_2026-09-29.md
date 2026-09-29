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

### Execution gate — 2026-09-29

Exact-head CI run `36521751170` (run #22) completed **SUCCESS** on research commit `f0cfc47e1b3593eb01986d8245099f88cbe574e3`.

That run established only:
- exact target checkout and 4.3.4 package-version verification;
- `test/BountyNativeOrderBoundary.js`: **1 passing**.

It did **not** run the remaining resolver/isolation controls because the workflow at that commit had only the boundary-test step.

The workflow was expanded to run four independent controls:
1. `BountyNativeOrderBoundary.js`
2. `BountyNativeOrderIsolation.js`
3. `BountyResolverRewardBalance.js`
4. `BountyResolverUndercollateralizedReward.js`

Workflow expansion commit: `c455fe9ae5938b05163c58010052a03b8afa7d1d`.

A harness timing defect was then identified: resolver cancellation with a nonzero reward requires the configured cancellation delay after expiry. Both resolver tests had advanced only to `expiration`. This was a test defect, not a contract result.

The harness was corrected:
- `BountyResolverRewardBalance.js` → `0f684b3191636d2677d6028e61b14182ec638476`
- `BountyResolverUndercollateralizedReward.js` → `6fd8f86fc4476ec70d110a62b275bf7b85d19429`

The current research branch / PR head is `6fd8f86fc4476ec70d110a62b275bf7b85d19429`.

GitHub Actions run #28 (`36522855418`) is executing the corrected four-control matrix. Latest observed state:
- target-pin verification: **PASS**
- dependency installation: **IN PROGRESS**
- all four assertion steps: **PENDING**

Therefore the resolver experiment remains **UNKNOWN / OPEN**.

### Resolver adversary-model gate

The current public Immunefi scope names Limit Order Protocol as in scope, lists direct theft of user funds as an in-scope Critical impact, and says the program applies only to latest tags/releases. Its privileged-address exclusion explicitly names governance and strategist, but does not name resolver/access-token-holder roles.

1inch Fusion documentation describes resolvers as professional market makers and the KYC/access token as the mechanism gating resolver participation.

Current classification:
- **ESTABLISHED:** resolver is a permissioned operational actor.
- **INFERENCE / OPEN:** the published bounty language does not explicitly classify resolver/access-token holders as the excluded privileged-address category.

This is not an `IN-SCOPE` determination. Economic impact, adversary eligibility, and audit/known-issue reconciliation remain separate gates.

### NativeOrder economic hypothesis — resolver reward vs undercollateralized balance

Static review + local harness design isolate H-E2: when maker collateral (C) is below resolver reward cap (R), an external WETH top-up of (R-C) can make the clone balance exactly (R). The cancellation path can then pay (R) to the resolver from the clone balance, leaving zero from that cancellation balance for the maker.

This remains a **behavioral hypothesis**, not a confirmed vulnerability, profitability claim, severity, or eligibility determination.

The production-like gate used by the contract is resolver possession of an access token; the local tests mint the mock token solely to construct the controlled execution environment.

### Audit coverage correction

The public 1inch audit archive evidence currently used in this research identifies the v4.3.4 audit entry with the **Permit2Proxy extension**. NativeOrderFactory and NativeOrderImpl are present in the 4.3.4 code, but current evidence is insufficient to mark their audit coverage as established.

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
`target pin PASS → boundary PASS → full resolver/isolation matrix PENDING`

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
