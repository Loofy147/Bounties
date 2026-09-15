# Control Plane Atomic Admission v0.1

Status: **Local multi-process reference gate — not production**

## Purpose

Ownership and pessimistic budget reservation must describe one authorization decision. If they are admitted independently, a worker can hold execution authority without the corresponding resource reservation, or a rejected owner can leave budget reserved.

This gate therefore establishes a single SQLite transaction boundary for:

```text
effect_key
   +
owner_id / fencing token
   +
budget reservation
   ↓
one durable admission transaction
```

## Safety properties

### A1 — Atomic admission

A claim is successful only if both ownership and budget reservation are committed. Any admission failure leaves neither newly granted ownership nor newly granted reservation.

### A2 — Single owner under contention

For one `effect_key`, the durable primary key plus `BEGIN IMMEDIATE` transaction serializes competing claims. At most one claim can retain active ownership.

### A3 — Budget ceiling conservation

The authority checks:

`reservation <= ceiling - reserved - consumed`

inside the same transaction that grants ownership.

### A4 — Expiry replacement is atomic

When an existing owner has expired, its outstanding reservation is removed and the replacement owner receives a newer fencing token within the same transaction.

### A5 — Stale owner rejection

The current `(effect_key, owner_id, fencing_token)` tuple is required for validation and release. A previous owner cannot release or validate after replacement.

### A6 — No implicit external-effect settlement

The authority never marks an external effect as successful or failed. It only controls local authorization ownership and budget reservation. `UNKNOWN` semantics remain owned by the effect protocol and executor reconciliation layer.

## Transaction boundary

The critical operation is:

```text
BEGIN IMMEDIATE
    read budget
    read effect ownership
    reject revoked/active owner
    expire old owner if necessary
    verify budget headroom
    write ownership
    write reservation
COMMIT
```

`BEGIN IMMEDIATE` is deliberately used for the local multi-process reference so competing writers cannot independently validate the same budget headroom and then both commit conflicting reservations.

## Failure semantics

The implementation is intentionally fail-closed:

- active ownership → claim rejected;
- revoked ownership → claim rejected;
- insufficient budget → claim rejected with transaction rollback;
- stale owner/token → validation/release rejected;
- expired ownership → execution authority is invalid and replacement may receive a newer fence.

A crash before commit must not be treated as evidence that an external effect failed. The eventual production design must preserve the distinction between authorization state and external outcome.

## Reservation lifecycle

For the reference model:

```text
claim        → reservation becomes RESERVED
release      → reservation returns to AVAILABLE
expiry+claim → old reservation released + new reservation acquired atomically
```

The model does not yet settle actual consumption. That remains a later effect-lifecycle transaction because committing an external effect and settling its actual cost require a separate executor contract.

## Why this gate matters

This phase closes a subtle gap between two otherwise-correct components. A correct fencing protocol without resource atomicity can admit an owner that has no budget capacity. A correct budget governor without ownership coupling can reserve resources for a worker that loses execution authority.

The desired invariant is therefore:

`effective execution authority => corresponding durable reservation`

within the same admission transaction.

## Explicit limits

This is not yet a production distributed lock service. The reference boundary still depends on:

- SQLite as a single local durable authority;
- local database availability;
- wall-clock time for expiry;
- executor-side enforcement of fencing;
- a future durable provenance integration;
- future policy/capability/lease binding.

It does not claim:

- exactly-once external effects;
- external-system fencing;
- consensus across independent database replicas;
- safe clock behavior under arbitrary clock rollback;
- atomic coupling to a real external payment/network/API side effect.

## Exit criteria for this phase

This gate is considered locally implemented when:

1. concurrent processes contend on one effect identity and one budget;
2. exactly one claim succeeds;
3. the budget reflects exactly one reservation;
4. a rejected claim leaves no partial reservation;
5. expiry recovery receives a higher fence without double reservation;
6. stale owners cannot validate or release;
7. the result survives reopening the SQLite authority.

The next gate is PEP/executor admission binding to the durable ownership token, not scheduler or Hunter integration.
