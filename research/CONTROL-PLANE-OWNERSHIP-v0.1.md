# Control Plane Effect Ownership v0.1

Status: **Local reference implementation — research gate**

## Purpose

The effect protocol established stable effect identity, explicit lifecycle states, and a fail-closed rule for `UNKNOWN` outcomes. The next unresolved safety property is concurrency: multiple workers must not become simultaneously authorized to execute the same effect.

This gate therefore introduces a narrow ownership authority around the stable `effect_key`.

The implementation is intentionally local-only. It does not claim distributed consensus, external side-effect atomicity, exactly-once execution, or production-grade persistence.

## Security property

For any `effect_key` there must be at most one active execution owner at a time.

A worker is considered current only when all three values match the authority's current record:

- `effect_key`
- `owner_id`
- `fencing_token`

A stale worker must be rejected even when it still holds an earlier owner credential.

## Ownership model

Lifecycle:

`UNOWNED → OWNED → RELEASED`

`OWNED → EXPIRED → OWNED`

`ANY VALID STATE → REVOKED`

Expiration is detected by the authority when a claim or validation operation observes that the ownership deadline has elapsed. A new claim after expiry receives a strictly higher fencing token.

Revocation is terminal for the reference model: future claims are rejected and the previous owner can no longer validate.

## Fencing

The fencing token is monotonically increasing per `effect_key`.

Example:

`worker-A / token 4` → expiry → `worker-B / token 5`

Even if worker A later resumes, token 4 is stale and must fail validation. This prevents a crashed or partitioned worker from remaining logically valid after recovery ownership is granted.

The token is an ownership guard, not a proof that an external system will honor fencing. An actual executor must bind the token into its authoritative execution-admission path.

## Atomicity boundary

The claim operation is serialized under one local lock. Therefore the reference implementation can demonstrate the following local property:

`N concurrent claims for one effect_key → exactly 1 successful active claim`

This is **not** equivalent to distributed atomicity. A production implementation requires a shared durable authority with an atomic compare-and-swap or transaction boundary and a failure model that explicitly covers worker crashes, process restarts, storage failover, and clock behavior.

## Recovery

Recovery after worker loss is intentionally time-based in this reference model:

1. The original owner acquires `token = T` with an expiry deadline.
2. The owner disappears without releasing the effect.
3. A later authority operation detects expiration.
4. Recovery worker claims the same effect and receives `token = T+1`.
5. Any attempt using the old owner identity or token is rejected.

The control plane must still reconcile the effect lifecycle separately. Ownership recovery does not mean the external side effect is safe to replay. In particular, `UNKNOWN` remains an explicit reconciliation state.

## Revocation / kill semantics

Revocation invalidates current ownership and prevents new claims. A production kill switch must operate through an authority independent of the worker being stopped; this local module only models the authority-side invalidation rule.

## Budget relationship

Ownership is not itself a budget reservation. The intended production invariant is:

`one active effect owner ↔ one active reservation authority`

A later integration gate must atomically couple ownership acquisition with durable budget reservation so two workers cannot both acquire execution rights and reserve the same effect cost.

## Tests defined by this gate

The reference suite covers:

- simultaneous multi-threaded claims with one winner;
- duplicate active claim rejection;
- stale fencing token rejection;
- renewal requiring the current owner/token;
- release followed by a new fenced owner;
- revocation blocking future claims and current validation;
- recovery after expiry with a strictly newer token;
- invalid TTL rejection.

## Explicit non-goals

This gate does not yet provide:

- durable ownership storage;
- cross-process/distributed CAS;
- lease persistence across storage restart;
- clock/monotonic-time hardening;
- integration with the PEP execution path;
- atomic ownership + budget reservation;
- owner fencing at an external system;
- scheduler fairness;
- network or exploit execution.

## Exit criteria

This gate may be considered locally satisfied only when the implementation demonstrates:

`one effect identity → one active owner → stale owners rejected → recovery gets a new fence → revocation blocks ownership`

The next gate is durable shared ownership, where the same properties must survive multiple processes, restart, and concurrent storage transactions.
