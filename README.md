# Bounties

This repository is the durable workspace for protocol/security bounty research.

## Operating rule

**Never let bounty reconnaissance depend on the working tree of another project.**

Moirae remains the protocol-verification laboratory. This repository stores the independent bounty track: target selection, scope snapshots, audit maps, hypotheses, reproductions, evidence packages, submissions, and outcomes.

## Evidence discipline

Every candidate is classified as `RECONNAISSANCE`, `HYPOTHESIS`, `REPRODUCED`, `IN-SCOPE`, `SUBMITTED`, `ACCEPTED`, `PAID`, or `REJECTED`. A hypothesis is never promoted to a finding merely because it sounds plausible.

## Current objective

Obtain the first legitimate, externally accepted paid finding, regardless of payout size.

Latest opportunity ranking: [`OPPORTUNITY-RECHECK_2026-10-25.md`](OPPORTUNITY-RECHECK_2026-10-25.md). It rechecks the current official Immunefi pages, corrects SP1's live maximum to $15,000, and ranks high-cap no-KYC candidates including Sky, GMX, and Spark.

The PAU × Spotter stale external-price hypothesis is marked `HYPOTHESIS CONTRADICTED`; exact Grove AllocatorVault source and direct read-only Ethereum state at block 26,267,615 confirm the active Spotter uses the fixed `PIP_ALLOCATOR`, with Vat `spot = 1e27` and actual line about debt + the 150M USDS AutoLine gap. See [the source-to-deployment recheck](targets/sky/PAU-SPOTTER-STALE-PRICE-RECHECK_2026-10-25.md). The deployed SPUSDC PAU controller's live dispatch map has no `usds_*` selectors at block 26,267,615; its active integration list is `CCTP_FACET` + `ERC4626_FACET`. The legacy SLL controller points to a separate `ALLOCATOR-SPARK-A` vault—not Grove's `ALLOCATOR-GROVE-A`. This prevents conflating the two paths; version-to-audit reconciliation and the currently active multi-controller topology remain open. See [the PAU deployment/audit gap review](targets/sky/DEPLOYMENT-AUDIT-GAP-2026-10-25.md).

The existing 1inch Smart Contracts / Limit Order Protocol H-E2/K-04 candidate remains `HYPOTHESIS / HOLD`. Local reproduction is not equivalent to bounty eligibility; the reporting deadline and other eligibility gates remain uncleared. Do not repeat synthetic variants of the same mechanism. See [the 1inch audit and eligibility recheck](targets/1inch/AUDIT-AND-ELIGIBILITY-RECHECK_2026-10-20.md) and [the current opportunity ranking](OPPORTUNITY-RECHECK_2026-10-25.md).

## Hunter architecture

The reusable research engine is defined in [`research/BUG-HUNTER-FOUNDATION-v0.1.md`](research/BUG-HUNTER-FOUNDATION-v0.1.md).

The canonical model is:

```text
scope
→ target snapshot
→ attack-surface/state model
→ security invariant
→ hypothesis
→ controlled experiment
→ evidence
→ independent validation
→ impact
→ minimized counterexample
→ novelty/scope gate
→ human review
→ submission
```

The system is evidence-driven rather than report-volume-driven. AI components may generate and investigate hypotheses, but the research record remains provenance-aware and a human approval gate is required before external submission.

## Directory model

```text
bounties/
├── targets/           # bounty-specific dossiers and scope snapshots
├── evidence/          # deterministic evidence packages and minimized traces
├── submissions/       # submission-ready reports; no secrets
├── outcomes/          # triage, acceptance, rejection, payout records
└── research/          # cross-target methodology and reusable checklists
```

## Relationship to Moirae

Reusable reasoning pattern:

```text
specification
→ state model
→ invariant
→ adversarial execution
→ deterministic reproduction
→ minimized counterexample
→ evidence
```

Moirae develops this capability on distributed protocols. Bounty work tests transferability against real external systems.

## Safety boundary

All work must remain within the current bounty scope and permitted test environment. Do not test production assets or public networks when the program prohibits it. Do not publish secrets, private credentials, or harmful exploit instructions.

## Snapshot provenance

The initial material in this repository is a preservation snapshot derived from the Moirae bounty-track documents on branch `feat/abd-atomic-register` of `Loofy147/moirae` on 2026-09-02. The original Moirae documents remain untouched.
