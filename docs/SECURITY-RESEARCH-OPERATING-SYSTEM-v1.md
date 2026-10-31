# Evidence-Driven Security Research Operating System

**Version:** 1.0 architecture documentation
**Status:** proposed integrated operating model
**Repository:** `Loofy147/Bounties`
**Document purpose:** define what the repository is becoming, how its parts work together, what is already demonstrated, and which gates prevent unsupported security claims or unsafe external action.

## 1. Executive definition

This repository is the foundation of a human-supervised security research operating system for bounty work. It is not a branch browser, an exploit generator, or a general-purpose autonomous pentester.

Its unit of work is a **validated security claim**. A claim is valuable only when the target state is pinned, the scope permits the experiment, the suspected invariant is explicit, the behavior is reproduced in a controlled environment, the evidence is traceable, the impact is calibrated, and a human has reviewed the result before any external submission.

The system turns an open-ended question — “could this target be vulnerable?” — into a sequence of controlled state transitions:

```text
scope
→ target snapshot
→ attack-surface and state model
→ security invariant
→ hypothesis
→ experiment plan
→ controlled execution
→ evidence bundle
→ independent validation
→ impact analysis
→ minimized counterexample
→ novelty / known-issue / scope gates
→ human review
→ optional submission
→ outcome and learning
```

The language model is an implementation component of this loop. It is not the source of truth. The source of truth is the repository’s pinned target state, recorded observations, deterministic tests, and evidence ledger.

## 2. What the system is for

The system is intended to help a security researcher move from a permitted target and an uncertain observation to a defensible, reviewable decision. It supports five connected jobs:

1. **Research preparation:** identify a legitimate opportunity, pin the eligible release or deployment, compile scope and prohibited-action rules, and establish a baseline.
2. **Technical investigation:** map code and runtime surfaces, define invariants, generate falsifiable hypotheses, and run local or otherwise permitted experiments.
3. **Evidence management:** preserve commands, inputs, outputs, traces, state deltas, hashes, timestamps, and reproduction instructions so another reviewer can reconstruct the claim.
4. **Decision control:** keep reconnaissance, hypothesis, reproduction, eligibility, submission, acceptance, and payout as distinct states. A plausible mechanism cannot silently become a finding.
5. **Learning:** record killed hypotheses, harness defects, false positives, known issues, and detector limitations so future investigations improve rather than repeat the same work.

The system deliberately does **not** authorize testing production systems, bypass program rules, access private data, submit reports, or transmit a trade or other external action without the required human and program approvals.

## 3. Design principles

### Evidence before confidence
Every material conclusion must point to an immutable target reference and raw observations. Narrative reasoning can prioritize work, but it cannot replace a reproduction or a documented reason why reproduction is impossible.

### Gates instead of vibes
The system uses explicit promotion gates. `HYPOTHESIS` is not `REPRODUCED`; `REPRODUCED` is not `IN-SCOPE`; `IN-SCOPE` is not `SUBMITTED`; and `SUBMITTED` is not `ACCEPTED` or `PAID`.

### Immutable provenance
A source commit, release tag, deployment address, block, dependency lockfile, configuration snapshot, and test command are part of the claim. If any of those are ambiguous, the system records uncertainty instead of silently selecting a convenient state.

### Falsifiability and kill discipline
A good experiment has an expected observation and a discriminating failure condition. When the condition is not met, the hypothesis is killed or narrowed and the reason is preserved. False-positive closure is a successful research result.

### Local-first execution
The default security boundary is a local harness, isolated fork, test deployment, or other explicitly permitted environment. The system must reject an experiment whose requested target, network, traffic, identity, or action violates the active scope contract.

### Human approval at irreversible boundaries
Automated analysis may prepare a candidate, evidence bundle, or draft. A human must approve any action that could affect a third-party system, disclose a vulnerability, submit a report, publish an unpatched issue, or change durable external state.

## 4. Core domain objects

### Target Snapshot
An immutable record of what was actually investigated.

```text
snapshot_id
repository / application / deployed asset
source commit, release, image digest, or deployment block
locked dependencies and build metadata
environment and endpoint classification
acquisition timestamp and provenance
scope_contract_id
```

A snapshot is invalid for promotion if the tested code cannot be mapped to the eligible target or if the runtime state is not reproducible.

### Scope Contract
A machine-readable boundary compiled from the official program rules and local authorization.

```text
in-scope assets and impacts
excluded assets and impacts
permitted techniques and environments
rate, traffic, identity, and data constraints
production / test / fork boundary
disclosure and reporting rules
human approval requirements
```

The executor checks the scope contract before starting an experiment. A contract is not inferred from a bounty title or a third-party summary.

### Attack-Surface Graph
A structured map of assets, entry points, functions, storage, roles, callbacks, extensions, dependencies, configuration, cryptographic domains, and externally observable effects. Each hypothesis references the smallest subgraph it needs.

### State Model
The minimum state transition model for a target:

```text
(State, actor, input, environment) → (State', effects)
```

It should identify balances, permissions, nonces, lifecycle states, configuration, external calls, and relevant ordering. For smart contracts, the model normally includes storage deltas, emitted events, token movements, call traces, and block/time assumptions.

### Security Invariant
A property that must remain true for every permitted execution in the threat domain. Examples include:

- an unauthorized actor cannot cause a protected effect;
- cumulative payout cannot exceed the authorized amount;
- cancelled or invalidated orders cannot settle;
- nonce and lifecycle state are monotonic and cannot be bypassed;
- a signature binds to the intended domain, operation, and deployment;
- assets are conserved across settlement;
- voting power or collateral value cannot be created by same-transaction manipulation.

The invariant gives the system a family of tests instead of one fragile exploit script.

### Hypothesis Record
A hypothesis is a structured, falsifiable object:

```text
hypothesis_id
target_snapshot_id
scope basis and current evidence status
affected surface and invariant
attacker capability and preconditions
expected vulnerable transition
experiment plan and stop condition
required evidence
status and next gate
kill / rejection reason, when applicable
```

### Experiment Record
An experiment records the exact command, input, fixture, actor identities, environment, expected result, observed result, and whether the harness itself was valid. A failed assertion is not automatically a protocol failure; harness defects are recorded separately.

### Evidence Bundle
Evidence is append-only and provenance-aware. A bundle can contain source and configuration hashes, commands, stdout/stderr, HTTP transcripts, transaction hashes, blocks, event data, storage or balance deltas, traces, screenshots where structurally insufficient evidence needs visual context, and reproduction instructions.

### Decision Record
A decision record promotes, narrows, kills, or defers a candidate. It must state the evidence used, unresolved uncertainty, the next discriminating action, and the person responsible for approval.

## 5. System components

### Scope Compiler
Transforms official program information, scope pages, release rules, reporting windows, and authorized test-environment rules into a scope contract. It must preserve page dates, asset-added dates, prohibited actions, KYC/reporting requirements, and the exact eligible release mapping.

### Target Snapshotter
Pins source, dependencies, deployment metadata, network, block, and configuration. It prevents the common failure where a technically valid result is tested against a non-eligible or moving target.

### Surface Mapper
Builds the attack-surface graph from source trees, ABIs, route specifications, deployment metadata, tests, configuration, documentation, and permitted runtime observations. It labels facts separately from inferences.

### Invariant Compiler
Converts source semantics, interfaces, state models, threat models, and scope into candidate invariants and test strategies. This is the bridge from code reading to systematic adversarial testing.

### Hypothesis Generator
Uses trust-boundary mismatches, authorization asymmetries, accounting edges, parser ambiguity, state-machine inconsistencies, stale state, ordering, configuration, upgrade boundaries, and known classes to generate candidates. Generation is cheap; promotion is expensive.

### Experiment Planner and Executor
Turns one hypothesis into a controlled experiment. The executor provisions only the allowed local or fork environment, checks preconditions, runs the deterministic harness, records outputs, and refuses a request that violates scope or approval state.

### Detector and Static Analysis Layer
Runs stock tools where useful and maintains custom checks for repeated trust-boundary questions. The reentrancy lab demonstrates this pattern with custom checks for unbound signatures, unprotected initializers, raw-balance valuation, live-balance voting, and unbounded swaps. The tooling also states the remaining no-TWAP oracle-manipulation gap instead of claiming coverage it does not have.

### Evidence Ledger
Maintains the current state of every candidate and the exact next gate. The current ledger uses:

```text
RECONNAISSANCE
→ HYPOTHESIS
→ REPRODUCED
→ IN-SCOPE
→ SUBMITTED
→ ACCEPTED
→ PAID
```

Rejected and killed candidates remain recorded with reasons.

### Validator and Impact Analyzer
Independently checks that the reproduced behavior is real, the target mapping is valid, the impact is within the program’s language, and the counterexample is minimized. It separates technical reachability from bounty eligibility and attacker economics.

### Report Builder
Produces a review package from evidence rather than from a free-form narrative. It includes affected version, preconditions, exact reproduction, observed impact, scope basis, known-issue/audit reconciliation, limitations, and unresolved questions. Submission remains a human action.

### Feedback and Learning Layer
Records accepted findings, rejected reports, false positives, killed hypotheses, harness defects, detector misses, and reviewer corrections. Future prioritization and detector changes must cite those records rather than silently modifying conclusions.

## 6. Repository mapping

The current repository already contains important pieces of this architecture:

| Repository material | Operating-system role |
|---|---|
| `research/BUG-HUNTER-FOUNDATION-v0.1.md` | architecture baseline and canonical research loop |
| `research/EVIDENCE-LEDGER.md` | candidate state, evidence stages, and next gates |
| `CURRENT_STATUS_*.md` | opportunity and target-state snapshots |
| `targets/` | target-specific dossiers, scope, hypotheses, reproductions, and closure records |
| `reentrancy-lab/` | controlled smart-contract experiments, nine vulnerability classes, and measured outcomes |
| `reentrancy-lab/inspector.py` | reusable stock-plus-custom inspection entry point |
| `reentrancy-lab/detect_missing_domain_binding.py` | focused custom detector for replayable signatures |
| `reentrancy-lab/test/` | deterministic reference and configuration tests |
| `.github/workflows/` | repeatable CI execution and evidence-producing checks |
| control-plane feature branches | ownership, effect, admission, and concurrency hardening concepts |
| evidence-gate branches | authorization, integrity, and promotion-boundary tests |
| research branches | target-specific experiments, source reconciliation, and false-positive closure |

These are complementary capabilities, not one homogeneous codebase. The integration target is a common operating model and shared evidence contracts, while each target harness keeps its own domain-specific implementation.

## 7. Canonical operating workflow

### Phase A — Admit a target

1. Record the official program, scope, reporting, disclosure, and test-environment sources.
2. Pin the eligible asset, release, commit, deployment, and dependency state.
3. Create a scope contract and identify prohibited actions.
4. Create a target snapshot and baseline evidence package.
5. Stop if the target-to-program mapping is ambiguous.

### Phase B — Build the model

1. Map assets, roles, entry points, storage, dependencies, and external effects.
2. Write the state transition model.
3. Identify trust boundaries and attacker capabilities.
4. Compile candidate invariants.
5. Rank hypotheses by impact, reachability, novelty uncertainty, and experiment cost.

### Phase C — Investigate

1. Create a hypothesis with an explicit falsifier.
2. Build the smallest controlled fixture that tests the invariant.
3. Run static detectors and record both hits and misses.
4. Run dynamic, fuzz, reference-model, or fork tests only inside the scope contract.
5. Separate harness failures from target failures.
6. Capture raw evidence and hashes.

### Phase D — Validate and gate

1. Re-run the reproduction from a clean, pinned state.
2. Minimize the counterexample and remove accidental preconditions.
3. Calibrate victim impact, attacker capability, and economic assumptions.
4. Reconcile audits, known issues, release/deployment correspondence, and reporting deadlines.
5. Promote, kill, defer, or hold the candidate with a written decision.

### Phase E — Human review and outcome

1. A reviewer checks the evidence bundle and scope interpretation.
2. A reviewer decides whether a report is warranted.
3. A human authorizes any external submission through the permitted channel.
4. The outcome, triage response, acceptance/rejection, payout, and lessons are recorded.
5. Detector and workflow improvements reference the outcome record.

## 8. Safety and authority boundary

The system may reason, inspect, generate local experiments, run permitted analysis, and assemble evidence. It must not infer authorization from technical access. It must refuse or pause when:

- the target or release is not pinned;
- the experiment would touch a prohibited environment or third-party data;
- the requested action exceeds the scope contract;
- a privileged actor is required but the program’s eligibility treatment is unresolved;
- the evidence is only a static suspicion;
- a harness defect could explain the observation;
- an external report or disclosure would be generated without human approval.

The system should optimize for truthful uncertainty. “Not detected” is not “safe”; “reproduced locally” is not “eligible”; and “in-scope impact” is not “accepted report.”

## 9. Current demonstrated capabilities

The repository demonstrates the following capabilities today:

- evidence-led target and hypothesis tracking;
- explicit promotion stages and killed-hypothesis preservation;
- deterministic smart-contract exploit demonstrations across nine classes;
- measured balance, gas, call, storage, and economic outcomes;
- custom detector development where stock static analysis is insufficient;
- offline-friendly compilation and Slither integration;
- reference-model and configuration tests;
- CI-based repeatable execution;
- target-specific opportunity, scope, audit, deployment, and known-issue reconciliation;
- control-plane research around ownership, effects, admission, and concurrency;
- human review and submission as a separate final gate.

The repository does not yet constitute a single turnkey autonomous platform. The remaining integration work is to standardize machine-readable records, provide a shared executor interface, connect the evidence ledger to experiment outputs, and make the approval boundary enforceable in the orchestration layer.

## 10. Integration contract for future components

Any new detector, target adapter, agent, or workflow should provide:

```text
component_id and version
input schema and provenance requirements
scope checks and authorization requirements
deterministic command or execution contract
output schema with raw evidence references
failure and harness-defect classification
known limitations and false-positive behavior
human approval points
regression test or fixture
```

A component that cannot preserve provenance, scope, raw observations, and limitations is not ready to become part of the operating system.

## 11. Roadmap

### Near term

- Convert the evidence ledger and hypothesis records into versioned machine-readable schemas.
- Add a common experiment manifest and evidence-bundle directory convention.
- Give every detector a fixture corpus containing positive, negative, and known-limit cases.
- Make scope checks executable before local harnesses start.
- Add a validator command that checks target pin, evidence completeness, and status transitions.

### Medium term

- Build target adapters for Solidity, EVM forks, HTTP APIs, Move/zkVM targets, and configuration-heavy systems.
- Add a searchable evidence index across target snapshots, hypotheses, experiments, and decisions.
- Add controlled parallel research with explicit budgets, shared provenance, and independent validation.
- Use outcome records to prioritize hypotheses and identify recurring detector gaps.

### Long term

- Support compositional attack-surface and invariant graphs across contracts, off-chain services, bridges, and operators.
- Add counterexample minimization and regression generation from every accepted or killed candidate.
- Measure the system by validated claims, false-positive reduction, evidence completeness, and reviewer time saved — not by the number of generated hypotheses.

## 12. Final significance

The value of this system is not that it can produce more security suspicions. Security teams already have more suspicions than they can safely act on. The value is disciplined conversion: from uncertain observation to pinned state, from state to invariant, from invariant to controlled experiment, from experiment to evidence, and from evidence to a human-reviewed decision.

That architecture makes AI useful without making it authoritative. It preserves failed experiments as knowledge, keeps bounty eligibility separate from technical reachability, exposes detector blind spots, and creates a durable research memory that can improve across targets and vulnerability classes.

The repository is therefore best understood as an evidence-driven security research operating system under construction: a set of interoperable research, execution, validation, and governance components that make legitimate vulnerability discovery more reproducible, more auditable, and safer to operate.
