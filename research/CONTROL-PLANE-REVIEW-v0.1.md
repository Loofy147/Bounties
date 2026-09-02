# Control Plane Architecture Review v0.1 — Decision Record

## Review status

**Disposition: ACCEPT AS RESEARCH BASELINE; NOT READY FOR EXECUTION AUTONOMY**

The control-plane architecture is reusable and is a strong fit for the Evidence-Driven Bug Hunter. It should not yet be treated as a production security boundary.

## What is already strong

- policy/capability/enforcement separation;
- target-specific research isolation;
- evidence emitted during execution;
- explicit risk classes and human approval;
- budget enforcement outside the model;
- fail-closed intent;
- deterministic policy decisions;
- target snapshot/provenance requirements;
- explicit non-goals for unrestricted autonomous activity.

## Critical gaps to close before implementation is trusted

### CP-01 — Authorization/Execution Atomicity

A policy decision can become stale between decision and execution.

Required contract:

`Authorize(snapshot, action) -> execution lease`

The execution lease must bind:
- policy version;
- capability version/id;
- target snapshot/id;
- action digest;
- expiry;
- one-use or bounded-use semantics.

The enforcement point must consume the same lease, not re-evaluate a weaker approximation.

### CP-02 — TOCTOU / Target Identity

Hostname/IP validation is not enough when DNS, redirects, proxies, shared hosting, IPv4/IPv6, or service discovery can change between authorization and execution.

Required target identity:
- canonical target;
- resolved endpoint identity;
- protocol/port;
- resolution evidence;
- validation timestamp;
- redirect chain policy.

Where identity changes, re-authorize or deny.

### CP-03 — Revocation Propagation

ADR-008/Invariant I-07 require revocation, but propagation semantics are unspecified.

Define:
- maximum revocation latency;
- authoritative revocation store;
- cache invalidation;
- in-flight action behavior;
- lease cancellation;
- evidence of revocation enforcement.

### CP-04 — Kill Switch Independence

The kill switch cannot depend on the same scheduler, worker, or model it is intended to stop.

Minimum design:
- independent control channel;
- deny-by-default emergency state;
- durable activation record;
- worker-side enforcement;
- recovery requires explicit re-authorization.

### CP-05 — Provenance Integrity

Append-only evidence is not sufficient if the storage layer can be rewritten.

Required baseline:
- hash-linked event chain;
- immutable content-addressed artifacts;
- policy/capability/action digests;
- monotonic sequence numbers;
- tamper detection;
- explicit trust boundary for the evidence store.

Cryptographic signatures may be deferred, but the integrity model must be defined.

### CP-06 — Multi-Worker Duplicate Effects

I-12 states idempotency, but the concurrency protocol is unspecified.

Define:
- effect identity;
- deduplication authority;
- lease ownership;
- compare-and-swap/state version;
- retry semantics;
- crash recovery.

No non-idempotent security-sensitive action should rely on best-effort client-side coordination.

### CP-07 — Resource Reservation

A hard budget ceiling must account for pending reservations, not just settled spend.

State:

`available = ceiling - committed - reserved`

Reservations must be released/settled deterministically after success, failure, timeout, or cancellation.

### CP-08 — Untrusted Tool Output

The architecture treats agent output as untrusted, but tool output is not explicitly modeled as hostile input.

Tool output must be:
- typed;
- size-limited;
- provenance-tagged;
- isolated from policy authority;
- prevented from injecting policy/capability instructions.

Prompt injection must never change authorization state.

### CP-09 — Isolation Boundary

“Sandbox” and “replica” are currently logical labels.

Define the minimum isolation boundary for each risk class:
- process;
- filesystem;
- network namespace;
- credentials/secrets;
- container/VM;
- host boundary;
- data egress.

A higher-risk action must never silently fall back to a weaker boundary.

### CP-10 — Approval Non-Replayability

Approval must bind to one concrete action or action class plus target snapshot and expiry.

Approvals must not be replayable against:
- another target;
- another policy version;
- another capability;
- a modified action digest.

### CP-11 — Scheduler Safety Under Contention

Adaptive scheduling must not compromise safety or create unbounded starvation.

The scheduler needs explicit invariants for:
- fairness/bounded starvation;
- priority inversion;
- reservation ownership;
- preemption;
- duplicate resumes;
- trajectory state versioning.

### CP-12 — Secret Handling

Secrets/credentials are absent from the architecture contract.

Define:
- secret references rather than raw values in trajectories;
- scoped credential leases;
- redaction;
- no secrets in evidence artifacts by default;
- explicit secret-use audit records.

## Required state machines

Before implementation, define three independently testable state machines:

### Authorization lease

`PROPOSED -> AUTHORIZED -> CONSUMED -> EXPIRED | REVOKED`

### Trajectory

`NEW -> RUNNING -> PAUSED -> RESUMABLE -> COMPLETED | ABORTED`

### Finding

`OBSERVED -> REPRODUCED -> VALIDATED -> IN_SCOPE -> REVIEW -> SUBMITTED`

Every transition must have a deterministic precondition and provenance event.

## Required executable test families

The first control-plane test suite should contain:

1. scope bypass attempts;
2. stale authorization/TOCTOU;
3. expired/revoked capability;
4. budget race and reservation overcommit;
5. duplicate non-idempotent action;
6. worker crash/recovery;
7. scheduler preemption/resume race;
8. kill-switch during queued and in-flight work;
9. evidence tamper detection;
10. approval replay;
11. hostile tool output / prompt-injection simulation;
12. cross-target capability reuse;
13. target identity change between decision and execution;
14. policy version change during a trajectory.

## Recommended implementation order

### P0
- typed policy model;
- capability model;
- authorization lease;
- PEP;
- durable event/evidence chain;
- budget reservations;
- kill-switch;
- trajectory state machine.

### P1
- target identity resolver;
- revocation protocol;
- effect-id/idempotency layer;
- isolation profiles;
- approval binding;
- secret-reference handling.

### P2
- adaptive scheduler;
- model routing;
- progress estimator;
- exploration/exploitation;
- multi-worker scaling.

### P3
- symbolic/constraint-guided planning;
- large-scale autonomous exploration.

## Relationship to Hunter

The Control Plane should govern the Hunter, not become the Hunter.

`Hunter = research intelligence`

`Control Plane = authorization + scheduling + execution governance + provenance`

`Evidence = shared audit substrate`

Target-specific logic remains under `targets/<target>/`.

## Final decision

**Use this architecture.**

Do not merge it as “production-ready security infrastructure”.

The next implementation target is a deterministic **Control Plane Kernel v0.1** with no external-target autonomy. Prove its safety invariants locally first; only then attach the existing Hunter kernel and later controlled target adapters.
