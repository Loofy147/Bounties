# Security-Bounty Research Operating System — Gap Analysis and Integration Specification

**Audit date:** 2026-10-31
**Audited repository:** `Loofy147/Bounties`
**Baseline:** `origin/main` at `da2baad`, plus the active remote feature/research branches
**Purpose:** identify what is missing from the 12-capability system definition, distinguish integrated behavior from branch-local prototypes and prose, and define the contracts and acceptance criteria for the next version.

## 1. Executive finding

The repository has a strong research method and several high-quality prototypes, but it is not yet one functioning operating system. The current state is best described as:

```text
strong evidence-driven methodology
+ target-specific research memory
+ isolated evidence-gate prototype
+ isolated control-plane kernel prototype
+ isolated smart-contract lab
+ isolated invariant benchmark
− shared schemas and storage on main
− workflow/orchestration runtime
− retrieval and vector memory
− common experiment adapter
− enforceable human-QA interface
− integrated outcome/feedback loop
```

The central integration risk is **capability fragmentation**. Important work exists on branches such as `feat/evidence-gate-layer-v0.1`, `feat/control-plane-kernel-v0.1`, `feat/reentrancy-lab`, and `research/invariant-composition-benchmark-v0.1`, but those capabilities do not yet share a common runtime, record store, task model, artifact convention, or approval service.

The correct next objective is therefore not “add more branches” or “display the repository.” It is:

> Build a local-first, policy-bounded research operating system in which every target, model, hypothesis, experiment, artifact, decision, report, and learning event is a versioned object connected by provenance and governed by deterministic gates.

## 2. Status vocabulary

| Status | Meaning |
|---|---|
| `DEMONSTRATED` | An executable implementation and tests exist on a referenced branch or in the integrated tree. |
| `PARTIAL` | The behavior exists as prose, manual records, or an isolated prototype but is not a shared system capability. |
| `MISSING` | No repository artifact currently provides the capability. |
| `BLOCKED` | The capability depends on an unresolved policy, target, security, or integration prerequisite. |
| `PLANNED` | The gap has an ownerable design and acceptance criteria but no implementation yet. |

A branch-local prototype is not counted as integrated. A document describing a control is not counted as enforcement.

## 3. Audit of the 12 required capabilities

| # | Required capability | Current status | What exists | Gap that must be closed |
|---:|---|---|---|---|
| 1 | Select and scope a bounty target | `PARTIAL` / prototype `DEMONSTRATED` | Target dossiers, opportunity reviews, official-source notes, and `scope_diff.py`; the evidence-gate branch has versioned scope snapshots and fail-closed checks. | No integrated intake service, target queue, freshness scheduler, source-capture workflow, or canonical `Engagement` record on `main`. |
| 2 | Capture exact target and deployment state | `PARTIAL` | Status documents pin commits, tags, addresses, blocks, and environment details manually. | No universal `TargetSnapshot` schema, dependency/build digest capture, deployment resolver, fork manifest, or snapshot artifact store. |
| 3 | Model contracts, permissions, assets, dependencies, trust boundaries | `PARTIAL` | Strong narrative state-model method and target-specific analysis; control-plane branch has target identity and capability concepts. | No shared attack-surface graph schema, importer, graph query/index, dependency/SBOM capture, or trust-boundary review gate. |
| 4 | Define security invariants | `PARTIAL` / benchmark `DEMONSTRATED` | Foundation documents define invariants; invariant-composition benchmark detects 3/3 seeded synthetic defects and keeps 3/3 controls clean. | No target-derived invariant compiler, invariant registry, traceability from invariant to hypothesis/test, or coverage metric. Synthetic success is not target validation. |
| 5 | Generate attack hypotheses | `PARTIAL` | Manual hypotheses, target research, and vulnerability-class labs exist. | No structured hypothesis generator interface, retrieval-grounded prompt/context package, duplicate detection, prioritization, or falsifier/stop-condition validator. |
| 6 | Run controlled experiments, detectors, fuzzing, invariant tests | `PARTIAL` / lab `DEMONSTRATED` | Reentrancy lab contains nine exploit demonstrations and a detector; target tools and benchmark runners exist on branches. | No common `ExperimentManifest`, adapter API, sandbox profile, seed/retry policy, tool registry, artifact capture, or safety preflight across targets. Fuzzing is not a shared capability yet. |
| 7 | Collect reproducible evidence | `PARTIAL` / gate `DEMONSTRATED` | Evidence ledger and evidence-gate schema/CLI support pinned revisions, artifact paths, hashes, timestamps, and policy checks. | Gate artifacts are branch-local; no append-only evidence store, run manifest convention, provenance index, redaction policy, or automatic linkage from every experiment. |
| 8 | Kill false positives and distinguish hypotheses from findings | `PARTIAL` | Status vocabulary, false-positive closure documents, negative controls, and explicit “not a finding” language exist. | No enforced transition service, independent validator queue, kill-reason taxonomy, regression fixture generation, or repository-wide state consistency. |
| 9 | Assess impact, novelty, eligibility, bounty scope | `PARTIAL` | Target dossiers manually reconcile impact, audits, known issues, role eligibility, production correspondence, and reporting deadlines. | No impact model, novelty/known-issue evidence index, scope-change alert pipeline, deadline monitor, or decision trace that blocks invalid promotion automatically. |
| 10 | Produce human-review-ready report/submission | `PARTIAL` | Reports and status documents are written manually; evidence-gate checks human authorship and approval fields. | No report package generator, evidence-to-report traceability, redaction checker, review checklist service, approval UI, or submission handoff record. |
| 11 | Record outcomes and feedback | `PARTIAL` | Rejected hypotheses and research outcomes are preserved in Markdown. | No normalized `Outcome`/`Feedback` schema, triage timeline, reviewer labels, payout record, metric store, or linkage back to detectors, prompts, and routing decisions. |
| 12 | Improve detectors, workflows, memory, research strategy | `PARTIAL` / benchmark `DEMONSTRATED` | Synthetic invariant benchmark, lab limitations, branch decisions, and roadmap prose exist. | No closed learning loop, benchmark registry, model/prompt versioning, retrieval quality evaluation, cost/utility telemetry, or safe strategy update process. |

## 4. Platform and architecture gaps

The 12 capabilities require a platform around them. The preferred system architecture adds an LLM, retrieval, workflow/memory, and human QA. Those layers are currently missing or only specified.

### 4.1 LLM reasoning layer — `MISSING`

There is no repository-level model gateway, model registry, prompt/template registry, structured-output contract, tool-call trace, cost ledger, or model evaluation harness. The system needs:

- model-agnostic `ReasoningRequest` and `ReasoningResponse` records;
- explicit L0 deterministic, L1 lightweight, and L2 advanced routing;
- JSON-schema-constrained outputs for hypotheses, invariants, plans, and decisions;
- prompt/context provenance including retrieved object IDs and model version;
- token, latency, failure, and cost telemetry;
- a rule that LLM output can propose but never authorize an action;
- offline/local model adapters for privacy-sensitive work.

### 4.2 Retrieval and vector memory — `MISSING`

The repository has Markdown memory but no ingestion pipeline, chunk identity, embeddings, vector index, lexical fallback, retrieval evaluation, or citation enforcement. Required capabilities are:

```text
source files / run artifacts / decisions
→ canonical document records
→ chunking with stable IDs
→ embeddings + lexical index
→ metadata filters by target, revision, status, sensitivity
→ retrieval with citations and access policy
→ evaluation of recall, precision, freshness, and contamination
```

Retrieval must never silently merge evidence from different target snapshots. Every retrieved fact needs source path, revision, timestamp, and confidence/provenance metadata.

### 4.3 Workflow and orchestration engine — `MISSING`

There is no durable task graph, queue, retry policy, dependency handling, pause/resume state, or worker protocol. The system needs a workflow engine that can express:

```text
engagement intake
→ scope snapshot
→ target snapshot
→ surface map
→ invariant set
→ hypothesis batch
→ experiment fan-out
→ independent validation
→ impact/eligibility review
→ human QA
```

Each task must have an idempotency key, parent trajectory, budget reservation, allowed capabilities, timeout, retry classification, and durable result. A failed or `UNKNOWN` side effect must not be retried as a new action without reconciliation.

### 4.4 Hierarchical control and adaptive scheduling — `PARTIAL` in prose, `MISSING` in runtime

The control-plane research branch specifies governance, capabilities, budgets, leases, kill switches, provenance, risk classes, and L0/L1/L2 routing. It does not yet provide a durable multi-worker scheduler or hierarchical RL implementation.

The preferred hierarchy should be:

```text
Strategic controller: choose engagement phase and bounded objective
    ↓
Tactical controller: choose target surface, invariant family, or experiment class
    ↓
Worker: perform one typed, capability-bounded task
    ↓
Validator: assess result and update evidence state
```

A hierarchical Q-network or other RL policy may rank or schedule work, but it must not bypass deterministic scope, capability, budget, identity, or human approval gates. Rewards should prioritize validated evidence, useful hypothesis-space reduction, false-positive reduction, and reviewer time saved — not raw exploit claims or report volume.

### 4.5 Human-in-the-loop QA interface — `MISSING`

Human review exists as a principle and Markdown activity, not as an enforceable interface. The system needs a local dashboard or API that shows:

- target and scope provenance;
- current hypothesis state and blockers;
- experiment evidence and raw artifacts;
- independent validator result;
- impact/novelty/eligibility checklist;
- proposed report with citations and redaction status;
- exact approval payload and reviewer identity;
- approve, reject, hold, kill, and request-more-evidence transitions.

The UI must not expose a “submit automatically” path. Approval must be bound to the exact report digest, target snapshot, evidence set, policy version, and expiry.

### 4.6 Execution and sandbox layer — `PARTIAL`

Local scripts, labs, fork testing, and a local control-plane kernel exist on separate branches. There is no common executor contract or isolation-profile implementation. Required profiles include:

| Profile | Use | Required controls |
|---|---|---|
| `MODEL_ONLY` | synthetic invariant reasoning | no target code or network |
| `SOURCE_LOCAL` | static analysis/build/test | workspace confinement, no secrets by default |
| `CHAIN_LOCAL` | local EVM/VM fixture | deterministic seed, isolated RPC, bounded resources |
| `FORK_READ_ONLY` | permitted local fork analysis | pinned block, no public writes, endpoint allowlist |
| `HTTP_REPLAY` | local request replay | fixture-only endpoints, rate limits, no third-party data |
| `HUMAN_ELEVATED` | exceptional authorized action | explicit approval, short lease, kill switch, full audit |

The executor must report `PASS`, `FAIL`, `BLOCKED`, `KILLED`, `HARNESS_DEFECT`, or `UNKNOWN`; it must never collapse executor uncertainty into success.

### 4.7 Evidence, provenance, and security storage — `PARTIAL`

The evidence-gate branch is the strongest existing implementation, but it validates records rather than providing a durable evidence service. The integrated system still needs:

- append-only run and artifact manifests;
- content-addressed artifacts with SHA-256 or stronger digest policy;
- encrypted/private storage for embargoed findings;
- secret reference handling and redaction;
- retention and deletion policy;
- hash-linked provenance or signed event records;
- source authenticity and snapshot freshness checks;
- prompt-injection and hostile-tool-output isolation.

### 4.8 Observability and evaluation — `MISSING`

No integrated telemetry measures research quality. Required metrics include:

- scope violations and denied actions;
- evidence completeness and reproducibility rate;
- hypothesis promotion, kill, and false-positive rates;
- detector precision/recall on labeled fixtures;
- validator disagreement rate;
- time from discovery to evidence package;
- reviewer correction time;
- model token/cost/latency by task class;
- retrieval citation coverage and stale-context rate;
- scheduler utility, starvation, and budget adherence.

Metrics must be separated by target and snapshot so results from different releases are not conflated.

## 5. Repository integration findings

### What is already reusable

- `research/BUG-HUNTER-FOUNDATION-v0.1.md` provides the conceptual research loop and gates.
- `research/EVIDENCE-LEDGER.md` provides a live example of evidence progression and unresolved gates.
- `feat/evidence-gate-layer-v0.1` provides versioned JSON schemas, fail-closed validation, scope diffs, fixtures, and tests.
- `feat/control-plane-kernel-v0.1` provides local capability, lease, budget, kill-switch, target-identity, PEP, and provenance primitives, plus invariants and a hardening matrix.
- `feat/reentrancy-lab` provides a reusable smart-contract lab, nine exploit demonstrations, detector tooling, and OPSEC notes.
- `research/invariant-composition-benchmark-v0.1` provides seeded-defect/negative-control evaluation for synthetic invariant predicates.
- target branches provide source pinning, audit/known-issue reconciliation, false-positive closure, and production correspondence research.

### What is not integrated on `main`

The audited `main` tree is primarily Markdown research memory and target dossiers. It has no root `.github/workflows` directory, no shared `schemas/`, no shared `tools/` package, no control-plane package, no common test suite, and no integrated lab runtime. The branch prototypes must therefore be treated as candidate components, not as a delivered platform.

### The integration boundary

The first integration should be intentionally narrow:

```text
schemas/
tools/
control_plane/
experiments/
evidence/
workflows/
tests/
```

Do not begin with autonomous public-network execution, broad web scanning, or an RL optimizer. First integrate the record contracts, local gate validator, provenance/artifact convention, control-plane kernel, and a single local experiment adapter.

## 6. Required shared object model

The following objects are the minimum cross-component contract:

| Object | Required fields | Primary consumers |
|---|---|---|
| `Engagement` | id, program, owner, policy version, lifecycle, approval state | governance, scheduler |
| `ScopeSnapshot` | official sources, retrieval time, terms, assets, eligible releases, diff parent | scope compiler, gate |
| `TargetSnapshot` | repository/address, immutable revision, block/image, dependencies, build digest, environment | mapper, executor, evidence |
| `SurfaceNode` | id, type, locator, trust boundary, provenance | mapper, invariant compiler |
| `Invariant` | id, statement, assumptions, affected state, source citations, test strategy | hypothesis engine, benchmark |
| `Hypothesis` | id, invariant, attacker capability, falsifier, priority, status | orchestrator, reviewer |
| `ExperimentManifest` | id, target, environment profile, command, seed, limits, capabilities, expected result | executor, control plane |
| `RunRecord` | manifest digest, start/end, worker/model versions, result class, stdout/stderr references | evidence, validator |
| `EvidenceArtifact` | id, content digest, path/store URI, target revision, observed time, sensitivity | evidence plane, report builder |
| `ValidationDecision` | reviewer/validator, checks, blockers, decision, parent evidence digest | state machine, QA |
| `ReportPackage` | claim, impact, reproduction, scope, known issues, citations, redaction, digest | human reviewer |
| `Outcome` | submission/triage/acceptance/payout, timestamps, reviewer labels, reason | learning layer |
| `FeedbackEvent` | source outcome, detector/prompt/workflow version, correction, proposed change, approval | improvement loop |
| `ReasoningTrace` | model, prompt template, retrieved IDs, output schema, cost, confidence, tool proposals | LLM gateway, audit |
| `Trajectory` | parent tasks, phase, budget, risk, progress, pause/kill state | orchestrator, scheduler |

Every object must carry `schema_version`, `object_id`, `created_at`, `parent_ids`, `policy_version`, and provenance references where applicable.

## 7. Acceptance criteria for the next system version

The system is ready to call itself an operating system only when all P0 criteria are met:

### P0 — evidence and authority foundation

- [ ] Shared schemas are present on the integration branch and validate real repository fixtures.
- [ ] A target cannot enter `EXPERIMENT_READY` without a fresh scope snapshot and immutable target snapshot.
- [ ] Every experiment has a manifest, capability, environment profile, seed/limits, and artifact destination.
- [ ] The evidence-gate validator runs before and after an experiment and binds evidence to the target revision.
- [ ] The control-plane P0 hardening items have executable evidence: lease binding, stale identity rejection, revocation, kill switch, provenance tamper detection, duplicate-effect exclusion, pessimistic budget reservation, and explicit `UNKNOWN` reconciliation.
- [ ] No worker has direct access to an external target; all actions pass through a tested PEP.
- [ ] Human approval is required for report transition and is bound to the exact report/evidence/policy digest.
- [ ] CI runs schema, gate, control-plane, benchmark, and fixture tests without public-network access.

### P1 — research workforce

- [ ] A durable workflow runner can execute the canonical graph with pause/resume, retries, budgets, idempotency, and kill.
- [ ] A local retrieval service indexes repository records with target/revision/status filters and citation-preserving results.
- [ ] One LLM gateway supports structured hypothesis and invariant generation with trace/cost logging and deterministic fallback.
- [ ] One experiment adapter runs the reentrancy lab or a synthetic local benchmark through the common manifest contract.
- [ ] A human QA interface can review evidence, blockers, and a report package without allowing automatic submission.
- [ ] Outcomes and feedback are stored in normalized records and linked to the originating detector/model/workflow versions.

### P2 — adaptive improvement

- [ ] Detector and invariant benchmark registry supports positive, negative, seeded-defect, and regression fixtures.
- [ ] Retrieval, model routing, and scheduler metrics have reproducible evaluation runs.
- [ ] A bounded hierarchical scheduler improves validated evidence per unit cost against FIFO/static baselines without safety regression.
- [ ] Feedback can propose detector/prompt/workflow updates, but updates require tests and human acceptance before activation.
- [ ] Cross-target adapters preserve target-specific scope and state semantics rather than flattening all research into one generic exploit taxonomy.

## 8. Recommended implementation sequence

1. **Integrate records first:** bring the evidence-gate schemas/tools and control-plane contracts into one integration branch; add migration fixtures for current target records.
2. **Add the evidence store:** implement content-addressed artifacts, run manifests, redaction, and append-only provenance.
3. **Add one executor:** adapt the local reentrancy lab or invariant benchmark to `ExperimentManifest`; prove isolation and deterministic capture.
4. **Add the workflow runner:** implement the canonical research DAG with durable task state, budgets, retries, pause/resume, and kill.
5. **Add retrieval:** index Markdown, JSON, source snapshots, run records, and outcomes with stable citations and target filters.
6. **Add LLM gateway:** structured outputs only, model routing, trace logging, bounded context, and no authorization power.
7. **Add human QA:** review and approval interface for promotion and report packaging.
8. **Add learning:** outcome schema, benchmark registry, correction events, and measured updates.
9. **Add hierarchical scheduling last:** use the control plane to govern adaptive prioritization; never use RL as a security boundary.

## 9. Safety requirements for self-improvement

Self-improvement is allowed only inside a bounded proposal-and-validation loop:

```text
feedback/outcome
→ proposed detector/prompt/workflow change
→ isolated benchmark and regression suite
→ independent review
→ versioned candidate
→ explicit activation approval
→ monitored rollout
→ rollback if safety or evidence metrics regress
```

The system must not rewrite its own scope policy, approval rules, access capabilities, or external-action boundary based solely on model output or reward optimization. Those are governance-controlled configuration, versioned and human-approved.

## 10. Bottom line

The repository is not missing a grander description. It is missing the integration layer that turns excellent research practices and branch-local prototypes into one executable, evidence-preserving, policy-bounded workforce.

The immediate gap is therefore measurable: create the shared records, enforce the gates, connect one experiment adapter, add retrieval and workflow state, and provide human QA. Only after those foundations are tested should the system add broader agents, adaptive scheduling, local model routing, or reinforcement-learning strategy selection.
