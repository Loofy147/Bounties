# Bounties

This repository is the durable workspace for protocol/security bounty research.

## Operating rule

**Never let bounty reconnaissance depend on the working tree of another project.**

Moirae remains the protocol-verification laboratory. This repository stores the independent bounty track: target selection, scope snapshots, audit maps, hypotheses, reproductions, evidence packages, submissions, and outcomes.

## Evidence discipline

Every candidate is classified as `RECONNAISSANCE`, `HYPOTHESIS`, `REPRODUCED`, `IN-SCOPE`, `SUBMITTED`, `ACCEPTED`, `PAID`, or `REJECTED`. A hypothesis is never promoted to a finding merely because it sounds plausible.

## Current objective

Obtain the first legitimate, externally accepted paid finding, regardless of payout size.

Latest source-verified opportunity review: [`CURRENT_STATUS_2026-10-20.md`](CURRENT_STATUS_2026-10-20.md). It records the 2026-10-14 1inch scope change, the release/eligibility gates, and the SP1 fallback assessment.

Current B0 target: 1inch Smart Contracts / Limit Order Protocol, but the existing H-E2 candidate remains a hypothesis and is on hold pending scope-to-release, audit/known-issue, role, production-impact and reporting-deadline gates. See `targets/1inch/` and the latest status snapshot.

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


## Reusable research layer

The first reusable software layer is being developed on the feat/evidence-gate-layer-v0.1 branch. Its goal is to make scope, target revision, claims, experiment constraints, evidence provenance, reporting deadlines, and human review gates machine-checkable.

See the Evidence Gate Layer v0.1 design in docs/EVIDENCE_GATE_LAYER_v0.1.md, the record schema in schemas/research-record-v1.schema.json, and the latest opportunity review in CURRENT_STATUS_2026-10-20.md. The validator never auto-promotes a hypothesis or submits a report; passing its gates is not proof of a vulnerability or a guarantee of bounty acceptance.

Run locally from the repository root with Python 3.12+:

    python -m unittest discover -s tests -v
    python -m tools.bounty_gate examples/claim-record.example.json --root . --pretty


## Scope snapshot diff (v0.2)

The structural diff utility compares manually reviewed, normalized snapshots; it does not scrape programs or assume that a changed page timestamp is a material scope change.

    python -m tools.scope_diff examples/scope-snapshot-before.example.json examples/scope-snapshot-after.example.json --pretty

The snapshots in the example are synthetic. See the v0.2 design section in docs/EVIDENCE_GATE_LAYER_v0.1.md.
