# Autonomous Security Control Plane — Implementation Roadmap v0.1

## Principle

Build the control system before increasing agent autonomy.

The first milestone is not exploit generation. It is proving that an autonomous worker cannot exceed its authority, budget, or evidence boundary.

## Phase 0 — Specification

Deliver:

- EngagementPolicy schema;
- Capability schema;
- Action schema;
- Evidence schema;
- Risk taxonomy;
- trajectory state machine;
- formal invariants.

Exit gate:

```
Schemas stable
Invariants testable
Trust boundaries documented
```

## Phase 1 — Control Plane Kernel

Implement:

- Policy Decision Point;
- capability verifier;
- budget governor;
- scheduler;
- trajectory store;
- kill switch;
- deterministic state transitions.

No autonomous external testing is required for this phase.

Exit gate:

- deterministic policy tests green;
- budget accounting tests green;
- recovery tests green;
- invariant suite executable.

## Phase 2 — Enforcement Plane

Implement:

- Policy Enforcement Point;
- network mediation;
- destination normalization;
- capability checks;
- rate controller;
- action audit records.

Exit gate:

- unauthorized targets rejected;
- revoked capabilities rejected;
- direct execution bypass impossible in the tested topology;
- fail-closed scenarios verified.

## Phase 3 — Evidence Plane

Implement:

- ActionRecord;
- EvidenceRecord;
- provenance chain;
- evidence hashes;
- trajectory snapshots;
- finding confidence state machine.

Exit gate:

- evidence completeness;
- replay metadata;
- durable parentage;
- reproducible state reconstruction.

## Phase 4 — L0/L1 Workers

Introduce deterministic and low-cost workers.

Focus on:

- parsing;
- normalization;
- state construction;
- differential observation;
- evidence organization.

Exit gate:

- workers operate exclusively through capabilities;
- no worker has unrestricted execution authority.

## Phase 5 — Adaptive Scheduler

Introduce:

- dynamic priority;
- exploration/exploitation;
- preemption;
- information-gain scoring;
- progress-aware eviction.

Evaluate against FIFO and static-priority baselines.

Exit gate:

- improved utility without safety regression;
- bounded starvation;
- predictable resource consumption.

## Phase 6 — Higher-Capability Reasoning

Introduce advanced reasoning only after the control and evidence planes are independently stable.

The reasoning layer receives:

```
state
evidence
capability
budget
policy
```

and returns proposed actions or hypotheses.

Exit gate:

- all actions remain mediated;
- no safety invariant regresses;
- model routing improves measured utility.

## Phase 7 — Controlled Target Integration

Use only explicitly authorized environments.

Begin with isolated replicas or local fixtures, then progress to narrowly scoped engagements according to the repository's existing bounty gates.

Exit gate:

- scope verified;
- novelty/audit gate verified;
- evidence independently reproducible;
- human submission gate intact.

## Phase 8 — Benchmarking and Research

Build a benchmark suite for:

- safety containment;
- scheduler utility;
- cost efficiency;
- evidence quality;
- recovery;
- model-routing efficiency.

The benchmark should compare architecture variants, not just individual models.

## Recommended Repository Placement

```
research/
├── CONTROL-PLANE-ARCHITECTURE-v0.1.md
├── CONTROL-PLANE-INVARIANTS-v0.1.md
├── CONTROL-PLANE-ROADMAP-v0.1.md
└── CONTROL-PLANE-DECISIONS-v0.1.md

targets/
└── <target>/
    └── target-specific research
```

The control plane remains target-agnostic. Target-specific scope, source snapshots, hypotheses, and evidence stay in their corresponding target dossier.
