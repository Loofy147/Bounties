# Control Plane Experiment Ledger v0.1

## Purpose

This document is the durable memory of the Control Plane work completed so far.

It exists to prevent repeated design loops over decisions that have already been reviewed, to distinguish proven local properties from open problems, and to define the exact next gate.

## 1. Architectural decision already settled

The reusable boundary is:

```text
Hunter Intelligence
    ↓ proposal
Security Control Plane
    ↓ authorization
Enforcement
    ↓ controlled admission
Execution
    ↓ observed effects
Evidence
```

The Control Plane is not a second Hunter. Hunter generates hypotheses and proposals; the Control Plane governs authority, resources, lifecycle, and execution safety.

## 2. What was rejected

### Rejected: LLM as security boundary

Reason: model output is probabilistic and can be affected by ambiguity, prompt injection, tool output, or reasoning errors.

Decision: deterministic policy, capability, lease, and enforcement checks own the hard boundary.

### Rejected: hostname-only scope validation

Reason: hostname does not uniquely represent the actual endpoint across DNS changes, IPv4/IPv6, redirects, service discovery, CDNs, and shared infrastructure.

Decision: typed target identity and authorization-time identity binding.

### Rejected: blind retry after uncertain execution

Reason: a timeout or worker crash after dispatch does not prove that an external effect did not occur.

Decision: explicit `UNKNOWN` state and mandatory reconciliation.

### Rejected: prompt-level budget control

Reason: an agent instruction cannot enforce a financial or compute ceiling.

Decision: external pessimistic budget reservation.

### Rejected: graph mutation as the only progress signal

Reason: negative evidence and hypothesis-space reduction can be meaningful progress without creating graph nodes.

Decision: progress includes knowledge, evidence, hypothesis-space, and state change.

### Rejected: zero-false-positive guarantee

Reason: sandbox/replica validation cannot prove universal production equivalence.

Decision: evidence-backed confidence with explicit environmental limitations.

### Rejected: early adaptive scheduler

Reason: scheduling complexity should not be layered on an unproven execution boundary.

Decision: finish P0/P1 control invariants before adaptive scheduling and multi-worker scaling.

## 3. Implemented layers

### Architecture baseline

`research/CONTROL-PLANE-ARCHITECTURE-v0.1.md`

Defines seven logical planes, capability model, scheduling model, resource governance, evidence plane, human governance, and safety invariants.

### Hardening review

`research/CONTROL-PLANE-REVIEW-v0.1.md`

Captured twelve critical gaps:

1. authorization/execution atomicity;
2. TOCTOU / target identity;
3. revocation propagation;
4. independent kill switch;
5. provenance integrity;
6. multi-worker duplicate effects;
7. resource reservation;
8. hostile tool output;
9. isolation boundary;
10. approval non-replayability;
11. scheduler contention/fairness;
12. secret handling.

### Kernel baseline

`control_plane/kernel.py`

Provides local-only deterministic policy/capability checks, leases, budget reservations, revocation, kill switch, trajectories, duplicate effect identity protection, and in-process provenance.

### Target identity hardening

`control_plane/target_identity.py`

Introduces typed target identity with a deterministic digest rather than hostname-only binding.

### PEP hardening

`control_plane/pep.py`

Requires exact lease/request binding and uses a kernel accessor rather than direct private-state access.

### Effect protocol

`control_plane/effects.py`

Introduces:

```text
AUTHORIZED
→ PREPARED
→ COMMITTED | FAILED | UNKNOWN
```

`UNKNOWN` cannot be blindly retried.

### Durable effect journal

`control_plane/durable_effects.py`

Provides a local JSONL crash-recovery reference model with state-transition validation, monotonic sequence checking, and hash-linked record integrity.

### Local fenced effect ownership

`control_plane/ownership.py`

Adds a narrow concurrency reference model around stable `effect_key` with one active owner, monotonic fencing, stale-owner rejection, expiry recovery, and local revocation.

### Durable shared ownership

`control_plane/durable_ownership.py`

Extends the fencing model across independent local processes using SQLite WAL and transactional `BEGIN IMMEDIATE` claim/update operations.

### Atomic ownership + budget admission

`control_plane/durable_budget_ownership.py`

Binds ownership acquisition and pessimistic budget reservation to the same SQLite transaction. Failed admission rolls back both; expiry replacement releases the old reservation and grants the new fence/reservation atomically.

`research/CONTROL-PLANE-ATOMIC-ADMISSION-v0.1.md` defines the contract and limits.

## 4. What has been learned from implementation review

### Lesson A — Lease binding is necessary but not sufficient

A lease can make authorization immutable, but it does not make an arbitrary remote side effect atomic.

The external boundary still requires executor-specific prepare/commit/reconcile semantics.

### Lesson B — In-process state is not production durability

Locks and dictionaries are sufficient for deterministic unit-level reasoning but do not survive process loss or coordinate independent workers.

A local SQLite reference is stronger evidence for multi-process serialization, but it remains a single local authority rather than a distributed consensus system.

### Lesson C — Evidence integrity has two layers

1. local tamper detection;
2. storage trust/durability.

A hash chain proves internal consistency only while the underlying trusted record history remains available. Production provenance therefore needs a defined trust boundary, persistence semantics, and recovery model.

### Lesson D — Authorization must bind to the exact action

A lease keyed only by target is insufficient. Binding must cover action identity and target identity; otherwise a valid lease can be replayed against a modified request.

### Lesson E — Ownership fencing is necessary but not sufficient

A fencing token can reject a stale worker at the Control Plane authority, but the check is not itself an atomic external execution fence.

The production execution path must bind ownership into the authoritative admission/commit boundary, otherwise a time-of-check/time-of-use window remains.

### Lesson F — Recovery ownership does not imply effect replay safety

After a worker crash, a new worker may safely acquire a newer ownership token without being allowed to assume that the previous external effect failed.

`UNKNOWN` therefore remains authoritative until executor-specific reconciliation determines the external outcome.

### Lesson G — Ownership and budget form one admission decision

Separating ownership and resource reservation creates an authorization gap. The local transactional reference therefore admits them together, so resource capacity and execution authority cannot diverge during the claim operation.

This closes the local admission gap but does not settle actual external-effect settlement, distributed failover, or production-grade transactional infrastructure.

## 5. Current guarantees

The current implementation is a **local deterministic reference kernel plus local SQLite concurrency references**.

It demonstrates the design direction for:

- fail-closed authorization;
- capability scoping;
- lease expiry/revocation;
- pessimistic budget reservation;
- duplicate effect identity rejection;
- kill-switch checks;
- exact local PEP binding;
- explicit UNKNOWN state;
- local crash-recovery journal semantics;
- provenance tamper detection;
- local single-owner effect claims;
- monotonic fencing and stale-owner rejection;
- expiry-based ownership recovery;
- local multi-process ownership serialization;
- atomic ownership + budget reservation at one SQLite authority.

These are reference properties, not production guarantees.

## 6. Current non-guarantees

Not yet proven:

- atomicity with a real external system;
- distributed consensus/shared ownership across independent authorities;
- crash-safe distributed revocation propagation;
- exactly-once effect execution across workers;
- durable production provenance;
- strong target-identity resolution against live infrastructure;
- isolation enforcement profiles;
- non-replayable approval protocol;
- secret-reference subsystem;
- hostile tool-output containment;
- scheduler fairness under contention;
- coupling of durable ownership into PEP/executor admission;
- actual cost settlement coupled atomically to external effect outcome.

## 7. Experiment status

| Experiment | Status | Conclusion |
|---|---|---|
| Scope rejection | Implemented | Unauthorized target must fail closed |
| Capability mismatch | Implemented | Principal/action/target mismatch denied |
| Lease expiry/revocation | Implemented | Unavailable lease cannot be consumed |
| Kill switch | Implemented | New and existing lease consumption blocked locally |
| Budget reservation | Implemented | Pending reservations count against ceiling |
| Duplicate effect identity | Implemented | Second authorization rejected locally |
| Exact PEP binding | Implemented | Target/action/effect mismatch rejected |
| UNKNOWN semantics | Implemented | Blind retry prohibited |
| Journal recovery | Implemented | State survives local reopen |
| Journal transition checks | Implemented | Invalid transitions rejected |
| Journal integrity | Implemented | Hash/sequence corruption detected locally |
| Local ownership claim race | Implemented | Concurrent local claims yield one active owner |
| Fencing / stale-owner rejection | Implemented | Older owner/token cannot validate after replacement |
| Ownership expiry recovery | Implemented | Recovery receives a strictly newer fencing token |
| Ownership revocation | Implemented | Revoked effect cannot be claimed or validated locally |
| Multi-process ownership claim | Implemented / unexecuted | SQLite transaction model and tests committed; runtime execution pending |
| Multi-process budget contention | Implemented / unexecuted | Independent effects cannot overbook the shared ceiling by design; runtime execution pending |
| Ownership + budget atomicity | Implemented / unexecuted | One transaction boundary defined; runtime failure-injection execution pending |
| Distributed concurrency | Open | Requires a shared durable authority beyond a single local database |
| External effect atomicity | Open | Requires executor-side protocol |
| Durable PEP ownership binding | Open | Next implementation gate |

## 8. Do not repeat these design loops

Do not reopen the following unless new evidence contradicts the decision:

- whether LLM prompts can enforce scope;
- whether hostname alone is sufficient target identity;
- whether UNKNOWN can be treated as FAILED;
- whether prompt text can enforce budgets;
- whether graph mutation alone defines progress;
- whether a sandbox can universally prove zero false positives;
- whether adaptive scheduling should precede P0 safety controls;
- whether the Control Plane should absorb Hunter intelligence.

These are settled architecture decisions for v0.1.

## 9. Next gate

The ownership and budget admission model is now implemented as a local transactional reference. The next unresolved boundary is **durable ownership binding at PEP/executor admission**.

Required sequence:

```text
Durable ownership + reservation
        ↓
PEP validates lease + target identity + action digest
        ↓
PEP validates current owner + fencing token
        ↓
Single admission decision
        ↓
Effect protocol PREPARE
        ↓
UNKNOWN / COMMITTED / FAILED reconciliation
```

The next phase must answer one precise question:

> Can an execution request that has lost or superseded ownership still reach the controlled execution admission boundary?

The target is prevention, not detection after the fact.

This phase must remain local-only and must not add network execution, exploit execution, adaptive scheduling, or Hunter integration.

## 10. Relationship to Hunter and H-A1

Hunter remains a proposal producer.

H-A1 remains target-specific research with its own evidence gates.

The Control Plane remains target-agnostic and local-only until its safety contract is proven.

No vulnerability conclusion should be inferred from Control Plane implementation status.

## 11. Reproducibility rule

Every future architectural change should record:

- hypothesis;
- invariant affected;
- implementation change;
- test introduced;
- result;
- remaining uncertainty;
- next gate.

This ledger is the memory boundary for the Control Plane workstream.
