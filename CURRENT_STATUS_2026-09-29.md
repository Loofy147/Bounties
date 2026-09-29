# Bounty Track Current Status — 2026-09-29

**Repository:** `Loofy147/Bounties`

## Current external status

The B0 target remains **1inch Smart Contracts**.

Current public program evidence checked on 2026-09-29:
- Program is live on Immunefi.
- Maximum bounty: $500,000.
- Proof of concept is required.
- KYC is required for payout.
- The program applies only to the latest tags/releases.
- Limit Order Protocol remains an in-scope asset.

The 1inch Limit Order Protocol repository currently identifies tag `4.3.2` as the latest production version that has passed security audits and explicitly warns not to use `master` as the production target.

## Local research status

Status remains:

`HYPOTHESIS`

No vulnerability has been established.

Previous snapshot:
- target tag: `4.3.2`
- target commit: `67c56aee3b6a9f4982bf487084bd8da1f6638da0`
- invariant families: fill accounting, invalidation, authorization/domain separation, parser/extensions/callbacks
- next research gate: executable local harness + mutation controls

## Re-verification gate

Before active testing or submission, re-pin:
1. current Immunefi program scope;
2. exact eligible release/tag and commit;
3. in-scope asset;
4. impact category;
5. known issues/audits;
6. permitted test environment and techniques;
7. reporting requirements.

No mainnet/public-testnet testing is authorized merely by this repository's existence. Follow the current program rules.

## Commercial role

Bounties is now an independent revenue channel alongside engineering contracts.

The success metric is not the bounty headline maximum. It is:

`RECONNAISSANCE → REPRODUCED → IN-SCOPE → SUBMITTED → ACCEPTED → PAID`

The first monetary milestone is one legitimate paid finding.

## Separation rule

- `Bounties`: external security research.
- `client-proof`: commercial engineering evidence.
- `proposals`: acquisition and sales control plane.
- `Open-System-One`: research laboratory.

Security research findings are never represented as client engineering experience unless independently applicable and accurately described.
