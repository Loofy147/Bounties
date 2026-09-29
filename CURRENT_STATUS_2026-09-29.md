# Bounty Track Current Status — 2026-09-29

**Repository:** `Loofy147/Bounties`

## Current external status

The B0 target remains **1inch Smart Contracts / Limit Order Protocol**.

Current public program evidence checked on 2026-09-29:
- Program is live on Immunefi.
- Maximum bounty: $500,000.
- Proof of concept is required.
- KYC is required for payout.
- The program applies only to the latest tags/releases.
- Limit Order Protocol remains an in-scope asset.

The 1inch repository has since published tag `4.3.4` (created 2026-09-24). The official 1inch audit archive now contains a dedicated OpenZeppelin audit entry for Limit Order Protocol v4.3.4. Because the live Immunefi program applies only to the latest tag/releases, `4.3.4` is the current working target; `4.3.2` is retained only as historical baseline context.

Current program constraints re-verified on 2026-09-29 include:
- testing must be performed on local forks; mainnet/public-testnet deployed code must not be tested;
- the program applies only to the latest eligible tag/releases;
- theoretical/speculative exploits without demonstrated business impact are out of scope;
- a PoC is required for all severities;
- a discovered vulnerability must be reported no later than 24 hours after initial discovery;
- AI-generated reports are prohibited.

These constraints are part of the B0 acceptance gate, not optional submission advice.

Sources: https://immunefi.com/bug-bounty/1inch-SmartContracts/scope/ and https://immunefi.com/bug-bounty/1inch-SmartContracts/information/.

## Local research status

Status remains:

`HYPOTHESIS`

No vulnerability has been established.

Previous snapshot:
- historical tag: `4.3.2`
- historical commit: `67c56aee3b6a9f4982bf487084bd8da1f6638da0`
- current target tag: `4.3.4`
- current target commit: `7da29889efa2e635611e1caf60f85f595ff7f05f`
- current tag object: `0a40e01befff19d925457b55191900fb456c2dd2`
- invariant families: fill accounting, invalidation, authorization/domain separation, parser/extensions/callbacks
- next research gate: executable local harness + mutation controls

## Re-verification gate

Before active testing or submission, re-pin:
1. current Immunefi program scope;
2. exact eligible release/tag and commit (`4.3.4` currently);
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
