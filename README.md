# Bounties

This repository is the durable workspace for protocol/security bounty research.

## Operating rule

**Never let bounty reconnaissance depend on the working tree of another project.**

Moirae remains the protocol-verification laboratory. This repository stores the independent bounty track: target selection, scope snapshots, audit maps, hypotheses, reproductions, evidence packages, submissions, and outcomes.

## Evidence discipline

Every candidate is classified as `RECONNAISSANCE`, `HYPOTHESIS`, `REPRODUCED`, `IN-SCOPE`, `SUBMITTED`, `ACCEPTED`, `PAID`, or `REJECTED`. A hypothesis is never promoted to a finding merely because it sounds plausible.

## Current objective

Obtain the first legitimate, externally accepted paid finding, regardless of payout size.

Current B0 target: 1inch Smart Contracts, beginning with a pinned production release of Limit Order Protocol. See `targets/1inch/`.

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
