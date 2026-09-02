# Policy-Bounded Autonomous Security Control Plane v0.1

## Status

**Document type:** Architecture Specification  
**Status:** Research baseline  
**Scope:** Reusable control-plane architecture for authorized security testing and bounty research  
**Safety posture:** Policy-bounded; no unrestricted autonomous network execution

## 1. Purpose

This document defines a Control Plane for autonomous security testing systems.

The design treats autonomous testing as a bounded feedback-control problem rather than an unconstrained reasoning loop.

The central rule is:

> The agent proposes work; policy, capabilities, enforcement, and evidence determine what may actually happen.

The architecture is intended to support authorized security research while preserving explicit scope, resource, impact, provenance, and human-governance boundaries.

## 2. System Objectives

The Control Plane must provide:

- scope integrity;
- capability-bounded execution;
- resource and monetary governance;
- adaptive prioritization;
- risk-aware model routing;
- execution mediation;
- failure containment;
- evidence provenance;
- reproducibility;
- human approval for elevated-risk actions.

It must not depend on model prompts, alignment behavior, or model refusals as the sole enforcement mechanism.

## 3. Architectural Model

```
┌──────────────────────────────────────────┐
│ Governance Plane                         │
│ Engagement / RoE / approvals / policy   │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│ Policy Decision Plane                    │
│ deterministic policy evaluation          │
│ capability authorization                 │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│ Control Plane                            │
│ Scheduler / Budget / Routing / State     │
│ Risk / Leases / Recovery / Kill Switch   │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│ Agent Runtime Plane                      │
│ L0 deterministic / L1 lightweight / L2  │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│ Enforcement Plane                        │
│ PEP / network mediation / action checks  │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│ Execution Plane                          │
│ isolated workers / sandboxes / replicas  │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│ Evidence Plane                            │
│ provenance / traces / artifacts / reports │
└──────────────────────────────────────────┘
```

These are logical planes. A minimal deployment may implement several planes in one service, provided their trust boundaries remain explicit.

## 4. Governance Plane

The engagement contract is represented as a machine-readable policy.

```
EngagementPolicy
 ├── engagement_id
 ├── authorized_assets
 ├── excluded_assets
 ├── identities
 ├── allowed_protocols
 ├── allowed_methods
 ├── allowed_ports
 ├── time_windows
 ├── rate_limits
 ├── budget_limits
 ├── action_classes
 ├── data_handling_rules
 ├── approval_requirements
 ├── evidence_requirements
 └── policy_version
```

Policy versions are immutable within an execution record. A policy change creates an auditable transition.

## 5. Policy Decision and Enforcement

### 5.1 Policy Decision Point

A proposed action is normalized and evaluated against:

- engagement policy;
- delegated capability;
- actor identity;
- target identity;
- action class;
- temporal constraints;
- current trajectory state.

Equivalent normalized inputs must yield deterministic decisions.

### 5.2 Policy Enforcement Point

The Policy Enforcement Point mediates every externally visible action.

No direct path from an agent to an external target is permitted.

```
Agent
  ↓
Action Proposal
  ↓
Policy Decision
  ↓
Capability Check
  ↓
Policy Enforcement Point
  ↓
Execution
```

### 5.3 Semantic Judge

A model-based judge may evaluate semantic ambiguity, intent drift, and trajectory risk.

It is an advisory control and is not the sole security boundary.

## 6. Capability Model

Workers receive narrowly scoped capabilities.

Conceptually:

```
Capability
 ├── capability_id
 ├── engagement_id
 ├── principal_id
 ├── target_set
 ├── allowed_actions
 ├── allowed_methods
 ├── allowed_protocols
 ├── rate_limit
 ├── budget_ceiling
 ├── expiry
 ├── risk_class
 └── evidence_requirements
```

A request is executable only when its normalized action is authorized by the active capability.

## 7. Priority and Scheduling Controller

Scheduling optimizes discovery utility under cost and risk constraints.

[
Priority(T)=
rac{
alpha hat R(T)
+eta hat I(T)
+gamma hat H(T)
+eta hat U(T)
}{
epsilon+hat C(T)
}
-deltahat L(T)
-hohat{Risk}(T)
]

Where:

- (hat R) = normalized expected security value;
- (hat I) = expected information gain;
- (hat H) = historical evidence signal;
- (hat U) = exploration value / uncertainty;
- (hat C) = expected computational and execution cost;
- (hat L) = latency penalty;
- (hat{Risk}) = operational risk.

All terms must be normalized before combining them.

Historical yield must not create an uncontrolled positive-feedback loop. Exploration remains explicitly bounded.

### Priority classes

| Tier | Mode | Scheduling behavior |
|---|---|---|
| P0 | Immediate | may preempt lower-risk work |
| P1 | High | priority allocation |
| P2 | Standard | normal queue |
| P3 | Background | yields resources under pressure |

Preemption serializes trajectory state so interrupted work can be resumed or retired.

## 8. Resource Governor

Every trajectory has independent limits:

```
TrajectoryBudget
 ├── token_limit
 ├── compute_limit
 ├── monetary_limit
 ├── network_request_limit
 ├── wall_clock_limit
 └── action_limit
```

Budget accounting is external to the agent.

A request to "stay under budget" in a prompt is not an enforcement mechanism.

## 9. Progress-Aware Eviction

Graph mutation alone is not a sufficient definition of progress.

[
Progress =
Delta Knowledge
+Delta Evidence
+Delta HypothesisSpace
+Delta State
]

Repeated actions with negligible progress may trigger:

- suspension;
- trajectory eviction;
- model downgrade;
- human review.

The stored trajectory remains available for audit and later replay.

## 10. Intelligence Routing

### L0 — Deterministic

Used for deterministic workloads such as parsing, normalization, state management, fixed transformations, and predefined validation.

### L1 — Lightweight Reasoning

Used for low-cost semantic work such as structural comparison, extraction, classification, and evidence organization.

### L2 — Advanced Reasoning

Used only where complex reasoning provides material expected utility.

Routing considers:

[
Route=f(Complexity,InformationGain,Risk,Uncertainty,Cost)
]

Model names and price points are intentionally not hard-coded into this architecture. They belong in dated benchmark records.

## 11. Network Scope Enforcement

All network activity is mediated.

Destination normalization must account for:

- hostname;
- DNS results;
- IPv4 and IPv6;
- ports;
- protocol;
- redirects;
- wildcard semantics;
- shared infrastructure;
- time-dependent scope.

Scope is therefore modeled as an authorization relation, not merely a domain/IP allowlist.

## 12. Rate and Service-Health Control

Telemetry may be used to detect service degradation and rate limits.

```
service-health signal
        ↓
rate controller
        ↓
backoff / pause
        ↓
policy evaluation
        ↓
resume / escalate / stop
```

Traffic adaptation does not constitute authorization to bypass engagement restrictions.

## 13. Impact Isolation

Higher-risk actions should use an isolated environment whenever practical.

Preferred order:

```
approved replica / synthetic environment
        ↓
controlled validation
        ↓
evidence capture
```

When environmental replication is not sufficient, the system records the limitation rather than treating a replica result as unconditional proof of production impact.

## 14. Evidence Plane

Every security-sensitive action generates a provenance record.

```
ActionRecord
 ├── engagement_id
 ├── capability_id
 ├── policy_version
 ├── principal
 ├── action_type
 ├── normalized_target
 ├── authorization_decision
 ├── execution_environment
 ├── request_reference
 ├── response_reference
 ├── timestamp
 ├── parent_action
 └── evidence_hash
```

The resulting causal chain is:

```
Policy
  ↓
Capability
  ↓
Action
  ↓
Observation
  ↓
Evidence
  ↓
Finding
```

## 15. Finding Confidence

The system must not represent verification as an unconditional Boolean.

```
FindingConfidence
 ├── observation_strength
 ├── repeatability
 ├── causal_support
 ├── environment_match
 ├── attribution
 ├── evidence_completeness
 └── residual_uncertainty
```

Recommended states:

- OBSERVED
- REPRODUCED
- STRONGLY_SUPPORTED
- ENVIRONMENT_LIMITED
- REQUIRES_HUMAN_VALIDATION
- UNCONFIRMED

The architecture therefore targets evidence quality and calibration rather than a universal zero-false-positive guarantee.

## 16. Core Control Loop

```
Target / Engagement
       ↓
Normalize Scope
       ↓
Construct Surface State
       ↓
Generate Signals / Hypotheses
       ↓
Score and Prioritize
       ↓
Select Capability
       ↓
Policy + Capability Decision
       ↓
Enforced Execution
       ↓
Capture Evidence
       ↓
Evaluate Progress / Risk / Budget
       ↓
Update State
       ↓
Repeat / Suspend / Escalate
```

## 17. Formal Safety Invariants

Minimum invariants:

### S1 — Scope

[
Target(a)in Scope(P)
]

### S2 — Capability

[
Action(a)in Capabilities(principal)
]

### S3 — Budget

[
Cost(	au)le Budget(engagement)
]

### S4 — Time

[
t(a)in AllowedWindow(P)
]

### S5 — Enforcement

[
ExternalActionRightarrow PEP(a)=true
]

### S6 — Provenance

Every security-sensitive action has an associated provenance record.

### S7 — Revocation

Revoked or expired capabilities cannot authorize new actions.

### S8 — Approval

Actions requiring human authorization cannot execute without an active approval record.

## 18. Human Governance

Risk determines autonomy.

| Risk class | Required control |
|---|---|
| R0 | autonomous within policy |
| R1 | autonomous + mandatory evidence |
| R2 | controlled execution + enhanced monitoring |
| R3 | explicit human approval |
| R4 | prohibited or separately governed |

Approval is itself a first-class evidence object.

## 19. Failure and Recovery

The system must remain safe under:

- worker crash;
- model timeout;
- scheduler failure;
- policy-service failure;
- network failure;
- duplicate execution;
- budget-state inconsistency.

Trajectory state should include:

```
Trajectory
 ├── graph_state
 ├── hypothesis_state
 ├── budget_state
 ├── capability_state
 ├── evidence_state
 └── execution_cursor
```

Security-sensitive operations require appropriate idempotency and duplicate protection.

## 20. Observability

Control-plane metrics should include:

### Scheduling

- queue latency;
- preemption rate;
- priority effectiveness.

### Resource governance

- cost per useful observation;
- cost per validated finding;
- token waste;
- budget violations.

### Safety

- blocked unauthorized actions;
- capability violations;
- policy failures;
- rate-limit events.

### Evidence

- evidence completeness;
- reproduction rate;
- confidence calibration.

### Agent efficiency

- useful action ratio;
- progress per step;
- context reuse.

## 21. Experimental Evaluation

The architecture should be evaluated by controlled benchmarks rather than qualitative claims.

Recommended comparison:

```
A — Unconstrained agent
B — Agent + static controls
C — Agent + Control Plane
D — Agent + Control Plane + adaptive scheduling
```

Measure independently:

- scope-violation rejection;
- budget containment;
- crash recovery;
- finding yield;
- validated-finding yield;
- cost per validated finding;
- information gain per action;
- provenance completeness;
- reproducibility.

No external-network or real-target experiment is implied by this architecture document.

## 22. Non-Goals

This specification does not define:

- a universal exploit-generation agent;
- unrestricted autonomous Internet activity;
- a mechanism for bypassing target-side controls;
- a guarantee of zero false positives;
- a production deployment without an explicit engagement policy;
- a specific LLM vendor or model.

## 23. Security Position

The architectural security boundary is the combination of:

[
Governance
+
Policy
+
Capabilities
+
Enforcement
+
Isolation
+
Evidence
]

Model alignment and model refusal behavior are not treated as authoritative security controls.

## 24. Relationship to the Bounties Research Kernel

This Control Plane is a reusable infrastructure layer for the repository's evidence-driven bounty workflow.

It complements the existing Hunter kernel:

```
scope
→ target snapshot
→ state model
→ invariant
→ hypothesis
→ controlled experiment
→ evidence
→ independent validation
→ impact
→ novelty/scope gate
→ human review
→ submission
```

The Control Plane governs how this workflow is executed; target-specific research remains under `targets/`.
