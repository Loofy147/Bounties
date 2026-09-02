# Control Plane Durable Effect Ownership v0.1

Status: **Local multi-process reference implementation — research gate**

## Objective

Carry the local ownership invariant across independent worker processes using a real transactional persistence boundary.

The property being tested is:

```text
one effect_key
→ one durable active owner
→ one fencing token generation
→ stale owner rejected
→ expired owner can be recovered with a newer token
```

SQLite with WAL mode is used as the reference persistence substrate. This is a local correctness experiment, not the final distributed architecture.

## Why this phase exists

The previous in-process authority used a `Lock` and Python dictionaries. That proves local thread serialization but does not coordinate independent processes.

A control-plane claim therefore needs an actual shared state boundary. The claim path in this phase uses a SQLite write transaction (`BEGIN IMMEDIATE`) around read/decision/update, so competing processes cannot both commit ownership for the same `effect_key`.

## Durable record

The reference table stores:

- `effect_key` — stable effect identity and primary key;
- `state` — ownership lifecycle state;
- `owner_id` — current worker identity when owned;
- `fencing_token` — monotonically increasing owner generation;
- `version` — durable state version;
- `acquired_at` — acquisition timestamp;
- `expires_at` — ownership deadline.

## Claim protocol

For one `effect_key`:

1. begin an immediate write transaction;
2. read the current durable record;
3. reject a non-expired `OWNED` record;
4. reject terminal `REVOKED` state;
5. convert an expired owner to `EXPIRED` when observed;
6. increment the effect's fencing token;
7. write the new `OWNED` record and expiry;
8. commit the transaction.

The uniqueness constraint on `effect_key` prevents duplicate durable registrations.

## Stale-owner rule

The execution authority must treat the tuple:

`(effect_key, owner_id, fencing_token)`

as the current ownership credential.

After recovery, an old owner has a lower fencing token and/or no longer matches the current owner. The authority rejects it.

This is a fencing mechanism at the Control Plane boundary. It does not prove that an arbitrary external service observes or enforces the token.

## Crash recovery

The reference model uses an expiry deadline rather than process heartbeat state.

A crashed process may leave `OWNED` state behind. A later claim observes the expired deadline, records `EXPIRED`, and assigns a strictly newer fencing token to the recovery owner.

This does not imply that the prior effect failed. An associated effect may still be `UNKNOWN` and require executor-specific reconciliation before any retry.

## Concurrency boundary

The current authority has two different guarantees:

### Proven by the model

Multiple independent local processes using the same SQLite database cannot successfully claim the same `effect_key` concurrently through this transaction path.

### Still open

This does not establish correctness across:

- distributed database replicas;
- filesystem/storage failure;
- clock anomalies across hosts;
- long-running transactions and process starvation;
- failover with different persistence semantics;
- external effect systems.

## Required gate tests

The reference suite targets:

1. six independent processes racing for one `effect_key`;
2. exactly one durable claim winner;
3. expiry followed by replacement with a newer fence;
4. stale old-owner rejection;
5. duplicate registration rejection;
6. revocation persistence across reopening the authority;
7. renewal/release requiring the current fencing credential.

## Critical remaining gap: ownership + budget atomicity

Ownership alone is insufficient if budget reservation occurs in a separate transaction.

The next integration must prevent:

```text
worker A claims effect
worker B claims effect
A reserves budget
B reserves budget
```

The intended invariant is:

`one effect owner ↔ one durable execution reservation`

That requires one authoritative transaction boundary or an explicitly recoverable transaction protocol for ownership and reservation.

## Critical remaining gap: execution TOCTOU

`assert_current()` is an authorization observation. It is not an atomic lock around an external side effect.

The final executor must either:

- perform the effect within an authority that honors the fencing credential;
- use a transactional prepare/commit boundary;
- or provide durable reconciliation semantics that make ambiguity explicit.

Blindly treating a successful ownership read as permission for an arbitrary external write would reintroduce the TOCTOU problem already identified by the hardening review.

## Non-goals

This phase does not add:

- remote target access;
- exploit generation or execution;
- scheduler adaptation;
- Hunter integration;
- exactly-once external execution claims;
- distributed consensus claims.

## Exit criteria

This gate is locally successful only if the multi-process tests show:

`one effect identity → one active durable owner → stale fence rejected → recovery gets newer fence → revocation persists`

Only after this is proven should ownership be coupled to budget reservation and the PEP's execution-admission path.
