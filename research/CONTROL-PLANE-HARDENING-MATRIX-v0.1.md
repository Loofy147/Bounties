# Control Plane Kernel v0.1 — Hardening Matrix

## Purpose

This matrix translates the 12 architecture gaps into explicit implementation contracts and executable test families.

| ID | Gap | Current kernel position | Required proof | Priority |
|---|---|---|---|---|
| CP-01 | Authorization ↔ execution atomicity | Lease binds authorization to exact action; external side-effect transaction not implemented | Executor protocol with PREPARE/COMMIT/UNKNOWN and crash-recovery semantics | P0 |
| CP-02 | TOCTOU / target identity | Typed `TargetIdentity` and digest binding added | Identity resolver + stale snapshot rejection + redirect/endpoint tests | P0 |
| CP-03 | Revocation propagation | Capability revocation invalidates unconsumed leases locally | Durable authoritative revocation protocol + bounded propagation latency | P0 |
| CP-04 | Independent kill switch | Separate local kill-switch primitive | Independent control path + queued/in-flight fault injection | P0 |
| CP-05 | Provenance integrity | Hash-linked events + immutable in-process payloads | Durable append-only store + tamper detection outside process memory | P0 |
| CP-06 | Duplicate effects | Effect identity is reserved before lease creation | Multi-worker atomic claim/CAS and crash recovery | P0 |
| CP-07 | Budget reservation | Pessimistic reservation exists | Concurrency tests + settlement/timeout/cancellation proof | P0 |
| CP-08 | Hostile tool output | Not yet modeled as a separate trust boundary | Typed/size-limited tool envelope; no policy mutation channel | P1 |
| CP-09 | Isolation profiles | Not yet implemented | Risk-class → isolation profile matrix and non-downgrade invariant | P1 |
| CP-10 | Approval non-replayability | Not yet implemented | Approval digest bound to action/capability/policy/target snapshot/expiry | P1 |
| CP-11 | Scheduler contention/fairness | Scheduler not yet implemented | bounded starvation, duplicate resume, reservation ownership tests | P2 |
| CP-12 | Secret-reference handling | No secret material in current kernel | Reference-only credentials, redaction, scoped leases, audit events | P1 |

## Critical State-Transition Contract

The architecture requires explicit state machines before remote execution:

### Lease

```text
PROPOSED
   ↓
AUTHORIZED
   ↓
PREPARED
   ↓
COMMITTED
   ├──> FAILED
   ├──> EXPIRED
   └──> REVOKED
```

`UNKNOWN` must be represented explicitly whenever the executor cannot determine whether an external effect occurred.

An `UNKNOWN` result cannot be silently retried as a fresh action. It requires effect reconciliation or a durable idempotency guarantee.

### Trajectory

```text
NEW → RUNNING → PAUSED → RESUMABLE → COMPLETED
                         ↘ ABORTED
```

Every transition requires a deterministic precondition and provenance event.

### Finding

```text
OBSERVED → REPRODUCED → VALIDATED → IN_SCOPE → REVIEW → SUBMITTED
```

## P0 Exit Criteria

The kernel must not be connected to Hunter or any external target until all P0 items have executable evidence for:

1. exact lease binding;
2. stale target identity rejection;
3. revocation behavior;
4. independent kill-switch behavior;
5. provenance tamper detection;
6. duplicate-effect exclusion;
7. pessimistic budget reservation under concurrency;
8. explicit UNKNOWN/reconciliation semantics for side-effect ambiguity.

## Current Boundary

This repository implementation remains a local reference kernel. It is suitable for testing authorization and accounting invariants, not for unrestricted autonomous execution.

The absence of a proven side-effect transaction protocol is intentional and must remain visible in future documentation and pull requests.
