# Evidence-Driven Bug Hunter — Foundation v0.1

**Status:** ARCHITECTURE BASELINE  
**Date:** 2026-09-02  
**Repository:** `Loofy147/Bounties`  
**Purpose:** Define the reusable security-research engine that will support the bounty track without coupling it to any single target or to the Moirae protocol repository.

---

## 1. Decision

We will not attempt to reproduce a commercial autonomous pentester by building a single general-purpose “hacking agent”.

The system will be built as an **evidence-driven vulnerability research engine** whose fundamental unit is a validated security claim backed by a reproducible state transition, request sequence, trace, or other deterministic evidence.

The canonical research loop is:

```text
Target + Scope
    ↓
Snapshot / Provenance
    ↓
Attack-Surface + State Model
    ↓
Invariant / Security Property
    ↓
Hypothesis
    ↓
Experiment Plan
    ↓
Controlled Execution
    ↓
Evidence Collection
    ↓
Independent Validation
    ↓
Impact Analysis
    ↓
Counterexample Minimization
    ↓
Novelty / Scope Gate
    ↓
Human Review
    ↓
Submission
```

A language model is an implementation component, not the source of truth.

---

## 2. Why this architecture

The main failure mode of AI-assisted security research is not inability to generate ideas. It is inability to reliably distinguish:

```text
plausible → reproducible → vulnerable → in-scope → reportable
```

The Hunter therefore treats each transition as a separate gate.

A candidate is never promoted because an agent says “this looks exploitable”. It is promoted only when the evidence required by its current state exists.

This is the security equivalent of the protocol-verification discipline already used elsewhere in the research program:

```text
specification
→ state model
→ invariant
→ adversarial execution
→ deterministic reproduction
→ minimized counterexample
→ evidence
```

---

## 3. Core objects

### 3.1 Target Snapshot

Immutable description of what was tested:

- repository / application / deployed asset
- exact commit, release, deployment, or image digest when available
- dependency lock state where relevant
- network endpoints and environment
- scope policy and allowed actions
- timestamp
- acquisition provenance

No security conclusion should depend on an unpinned or ambiguous target state.

### 3.2 Scope Contract

Machine-readable representation of:

- in-scope assets
- excluded assets
- permitted techniques
- rate and traffic constraints
- authentication requirements
- prohibited actions
- production/test environment boundary
- disclosure requirements

The executor must reject an experiment that violates the active contract.

### 3.3 Attack-Surface Graph

A graph connecting:

- assets
- endpoints
- handlers
- contracts
- functions
- storage/state
- identities/roles
- trust boundaries
- external dependencies
- callbacks/extensions
- cryptographic domains
- state transitions

Each hypothesis points to the subgraph it depends on.

### 3.4 State Model

For stateful targets, represent:

```text
State × Input → State'
```

with explicit actors, permissions, assets, and externally observable effects.

This is mandatory for protocol, smart-contract, authorization, accounting, transaction, and workflow targets.

### 3.5 Security Invariant

A property that must remain true under every permitted execution in the modeled threat domain.

Examples:

```text
unauthorized actor cannot cause protected effect
cumulative payout ≤ encoded/order-authorized amount
cancelled/invalidated order cannot settle
nonce/state monotonicity cannot be bypassed
signature binds to the intended domain + operation
asset conservation holds across settlement
state transition requires the required authority
```

An invariant is preferable to an isolated “bug pattern” because it gives the Hunter a family of adversarial experiments.

### 3.6 Hypothesis Record

Every hypothesis must contain:

- unique identifier
- target snapshot
- scope basis
- affected components
- invariant/security property
- attacker capability
- expected exploit condition
- experiment plan
- evidence requirements
- current status
- rejection reason, when rejected

### 3.7 Evidence Bundle

Evidence is append-only and provenance-aware. A bundle should contain, where applicable:

- exact target version
- exact command/request/input
- preconditions
- relevant configuration
- stdout/stderr or HTTP transcript
- state/storage deltas
- transaction hash / block / event data
- screenshots only when they add information not captured structurally
- timestamps
- hashes of artifacts
- reproduction instructions
- expected vs observed result

The claim must be traceable back to raw observations.

---

## 4. Engine components

### 4.1 Scope Compiler

Transforms the program policy into an executable scope contract.

Hard rule: **no experiment starts before a scope decision exists.**

### 4.2 Target Snapshotter

Pins the exact research state and records provenance.

For source targets this normally means commit/tag plus dependency state. For deployed targets it includes the exact permitted host/environment and relevant version evidence.

### 4.3 Surface Mapper

Constructs the attack-surface graph from:

- source tree
- ABI / interface definitions
- API specifications
- routes/endpoints
- deployment metadata
- configuration
- tests
- documentation
- runtime observations

It must distinguish discovered facts from inferred relationships.

### 4.4 Invariant Compiler

Converts target semantics into candidate security invariants.

Inputs:

```text
source + interfaces + state model + threat model + scope
```

Outputs:

```text
candidate invariant + affected state + attack preconditions + test strategy
```

This is a priority component because it turns one vulnerability hypothesis into a systematic search space.

### 4.5 Hypothesis Generator

Generates hypotheses from:

- violated or suspicious invariants
- trust-boundary mismatches
- authorization asymmetries
- accounting edge cases
- parser ambiguity
- state-machine inconsistencies
- race/order dependence
- stale-state interactions
- upgrade/configuration boundaries
- externally known vulnerability classes

Generation is cheap. Promotion is expensive.

### 4.6 Experiment Planner

Turns a hypothesis into the smallest safe experiment capable of falsifying or confirming it.

Priority order:

```text
static contradiction
→ local deterministic test
→ local harness
→ isolated test deployment
→ explicitly permitted remote test
```

The planner optimizes for information gain per unit risk/cost, not raw request volume.

### 4.7 Controlled Executor

The executor enforces:

- scope
- rate limits
- concurrency budgets
- target allowlist
- destructive-action policy
- authentication constraints
- experiment timeout
- artifact capture

It must be possible to replay an experiment deterministically where the target permits it.

### 4.8 Evidence Collector

Captures the minimum raw material required to reproduce and validate the observation.

No material observation is accepted without provenance.

### 4.9 Independent Validator

Validation must be logically separate from discovery.

The validator receives the hypothesis and evidence, but it must independently decide whether:

1. the observed behavior is real;
2. the behavior violates a security property;
3. the attacker can actually reach the condition;
4. the claimed impact follows;
5. the result is reproducible.

Where practical, discovery and validation should use different prompts, reasoning paths, or execution procedures to reduce correlated false positives.

### 4.10 Counterexample Minimizer

Given a successful exploit trace, reduce it to the smallest sequence preserving the security violation.

For example:

```text
47-step trace
→ 19-step trace
→ 8-step trace
→ 4-step minimal PoC
```

A minimal trace is easier to review, reproduce, report, and debug.

### 4.11 Impact Calculator

Separates “vulnerable” from “high impact”.

Impact must be derived from the actual effect:

- unauthorized asset movement
- unauthorized state mutation
- privilege escalation
- confidentiality loss
- integrity loss
- availability impact
- economic loss
- cross-user/cross-tenant impact

The system must not infer severity merely from the vulnerability class name.

### 4.12 Novelty Gate

Before submission, compare the candidate against:

- target advisories
- published audits
- changelogs
- known issues
- CVEs where applicable
- existing repository issues
- program disclosures where available
- prior local findings
- previously rejected hypotheses

The purpose is not to prove absolute global novelty; it is to prevent avoidable duplicate and already-known submissions.

### 4.13 Human Approval Gate

No submission is emitted automatically as a final action.

The human reviewer confirms:

```text
scope ✓
reproduction ✓
security impact ✓
novelty check ✓
policy compliance ✓
report accuracy ✓
```

The system may prepare the report, but the human remains accountable for the submission decision.

---

## 5. Finding state machine

```text
RECONNAISSANCE
      ↓
HYPOTHESIS
      ↓
REPRODUCED
      ↓
IN-SCOPE
      ↓
SUBMISSION-READY
      ↓
SUBMITTED
      ↓
ACCEPTED
      ↓
PAID
```

Negative outcomes are retained:

```text
HYPOTHESIS / REPRODUCED / SUBMITTED
      ↓
REJECTED
```

A rejection is valuable training/evaluation data and must not be silently deleted.

---

## 6. Security research strategy

The first implementation should prioritize **stateful, invariant-rich targets** rather than breadth-first web scanning.

High-value starting surfaces:

1. smart-contract accounting and authorization;
2. protocol/state-machine correctness;
3. authentication/authorization transitions;
4. transaction/settlement/reconciliation logic;
5. parser + extension/callback boundaries;
6. concurrency and stale-state interactions.

These surfaces match the strongest reusable reasoning pattern available to us: explicit state, invariants, adversarial schedules, and minimal counterexamples.

Web-scale coverage can be added later through adapters without changing the evidence kernel.

---

## 7. Benchmark before production

The Hunter is not considered operationally mature because it found one interesting bug.

It must first survive a controlled benchmark suite.

### Stage 0 — Mutation benchmark

Seed known defects into local targets and measure whether the Hunter kills the mutations.

Required properties:

- baseline must pass before mutation
- each mutation must be isolated
- failing behavior must be attributable to the mutation
- no test may be considered effective if the baseline is already red

### Stage 1 — Known vulnerable versions

Replay public vulnerable versions of projects and determine whether the Hunter can reproduce the known issue from scratch.

### Stage 2 — Hidden seeded vulnerabilities

Place previously unseen but realistic defects into target snapshots. The evaluator knows the defect; the Hunter does not.

This measures actual discovery rather than benchmark memorization.

### Stage 3 — CTF/local adversarial environments

Use isolated environments for multi-step exploitation, web, API, auth, and stateful chains.

### Stage 4 — Permitted bounty programs

Run bounded experiments only after scope and policy checks pass, with human validation before reporting.

### Stage 5 — Scale

Only after precision and evidence quality are stable should we optimize concurrency, target breadth, scheduling, and cost per validated finding.

---

## 8. Evaluation metrics

The primary metric is not “number of hypotheses generated”.

Track:

```text
precision = validated findings / submitted candidates
reproduction rate
novel-find rate
impact-accuracy rate
false-positive rate
median time to validated finding
cost per validated finding
minimal-PoC compression ratio
scope-policy violation count
duplicate/repeat rate
```

For bounty performance, also track accepted and paid findings separately from internal discoveries.

A large volume of low-signal reports is explicitly a failure mode, not a success metric.

---

## 9. Leaderboard strategy

The competitive objective should be decomposed into measurable milestones:

```text
first reproducible local exploit
→ first in-scope candidate
→ first accepted finding
→ first paid finding
→ repeatable accepted findings
→ high-impact findings
→ sustained signal
→ competitive leaderboard position
```

HackerOne's current 90-day leaderboard uses a score based on Reputation × Signal Percentile × Impact Percentile. Eligibility includes positive reputation gain, non-negative signal, and zero Code of Conduct violations. Therefore optimizing for raw report count is strategically wrong; the system must optimize for **validity and impact while preserving policy compliance**.

The current minimum bounty specified by HackerOne is $50. Therefore the project milestone is “first paid accepted finding”, not an arbitrarily tiny payout.

---

## 10. Responsible-automation boundary

Current HackerOne policy permits AI-assisted research but requires researchers to validate AI-assisted outputs and remain responsible for the submission. HackerOne's current Hackbot guidance explicitly requires a human-in-the-loop model and prohibits fully autonomous operation, unverified/fabricated claims, high volumes of low-signal reports, and unsafe or out-of-scope testing.

Consequences for this architecture:

```text
AI discovery: allowed
AI reconnaissance: conditional on program policy
AI exploit development: conditional on program policy
AI evidence analysis: allowed
AI report drafting: allowed
fully autonomous submission: prohibited
unreviewed claim submission: prohibited
```

Therefore the Human Approval Gate is not optional architecture decoration; it is a current operational requirement for HackerOne participation.

---

## 11. Relationship to the bounty repository

`Loofy147/Bounties` is the canonical workspace for the external-security track.

Rules:

- do not store bounty material in unrelated protocol PRs;
- preserve exact target versions and scope snapshots;
- keep hypotheses separate from confirmed findings;
- preserve rejected research;
- never mix secrets or credentials into the repository;
- keep reproducibility artifacts deterministic and reviewable;
- use the repository history as the research audit trail.

Moirae may contribute reusable verification techniques, but bounty execution remains independent.

---

## 12. First implementation boundary: Hunter v0.1

The first usable slice should contain only:

```text
scope compiler
+ target snapshotter
+ evidence schema/store
+ hypothesis ledger
+ deterministic experiment runner
+ validator
+ minimal PoC/reproducer
+ novelty gate
+ human approval gate
```

The following are deliberately deferred until the kernel is proven:

- large-scale autonomous crawling;
- 24/7 remote scanning;
- broad browser automation;
- autonomous submission;
- reinforcement-learning scheduling;
- massive multi-agent swarms;
- optimization for raw request throughput.

The kernel must become reliable before it becomes large.

---

## 13. First target application

The first external application of the Hunter remains the current B0 track:

**1inch Limit Order Protocol**, pinned to the verified production release `4.3.2`.

Initial audit order:

```text
A. fill/accounting invariants
B. invalidation/cancellation semantics
C. authorization + signature/domain binding
D. parser/extensions/callbacks
```

The research process remains:

```text
pin exact release
→ local baseline
→ one-order model
→ invariant families
→ deterministic harness
→ mutation checks
→ exploit hypotheses
→ evidence
→ minimal PoC
→ scope/novelty gate
→ human review
```

No vulnerability is presumed to exist. The target is currently a research target, not a finding.

---

## 14. Non-negotiable quality gates

A candidate must not become `SUBMISSION-READY` unless all applicable gates are green:

| Gate | Requirement |
|---|---|
| Target | exact version/state identified |
| Scope | program policy explicitly permits the tested asset/action |
| Preconditions | attacker capabilities are realistic and documented |
| Reproduction | deterministic reproduction exists or environmental nondeterminism is explicitly characterized |
| Security property | concrete invariant/security requirement is violated |
| Evidence | raw observations and provenance are preserved |
| Impact | effect is demonstrated, not inferred from labels |
| Novelty | known/public/repository duplicates checked |
| Minimality | PoC minimized as far as practical |
| Safety | no prohibited/destructive activity |
| Human review | researcher has independently validated the claim |

---

## 15. Research principle

The Hunter should be judged by this sentence:

> **It does not try to sound like a hacker; it tries to produce a security claim that another competent researcher can reproduce and verify.**

That is the foundation for scaling from a small bounty experiment into a serious security-research system.

---

## 16. External policy references checked 2026-09-02

- HackerOne Code of Conduct — Hackbots, AI-assisted research, human-in-the-loop, prohibited AI use: https://www.hackerone.com/policies/code-of-conduct
- HackerOne Hai Security & Trust — current Hackbot guidance: https://docs.hackerone.com/en/articles/10908081-hai-security-trust
- HackerOne 90-Day Leaderboard — eligibility and scoring: https://docs.hackerone.com/en/articles/8456917-90-day-leaderboard
- HackerOne Signal & Impact — validity/severity signals: https://docs.hackerone.com/en/articles/8369891-signal-impact
- HackerOne Awarding Bounties — current $50 minimum bounty: https://docs.hackerone.com/en/articles/8524543-awarding-bounties

These references are policy inputs, not substitutes for checking the individual program's current rules before each test or submission.
