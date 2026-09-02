# Control Plane Effect Protocol v0.1

## Status

Research specification; local-only reference semantics.

## Purpose

The authorization lease solves policy binding, but it does not by itself make a real external side effect atomic with authorization.

A concrete executor must therefore distinguish:

```text
AUTHORIZED
    ↓
PREPARED
    ↓
COMMITTED
```

with explicit failure states:

```text
PREPARED → FAILED
PREPARED → UNKNOWN
```

## Core rule

An `UNKNOWN` outcome is not permission to retry.

When a worker loses certainty after dispatch, the system must preserve the effect identity and require reconciliation against the external system before another attempt can be authorized.

## Effect Identity

Every potentially non-idempotent effect has a stable `effect_key` bound to the authorization lease.

The identity must survive worker restart and must not be regenerated merely because an execution attempt failed locally.

## State Machine

```text
AUTHORIZED
   │
   ▼
PREPARED ───────────────┐
   │                    │
   ├──► COMMITTED       ├──► UNKNOWN
   │                    │
   └──► FAILED          │
                        │
                        ▼
                 external reconciliation
                        │
                 resolved outcome
```

`UNKNOWN` remains non-terminal from the perspective of the overall engagement, but it is terminal for blind retry. A reconciler must establish the external outcome before a new effect attempt may be considered.

## Atomicity Boundary

The following is guaranteed by the local kernel:

```text
policy decision
    ↓
capability validation
    ↓
budget reservation
    ↓
immutable execution lease
    ↓
exact execution binding
```

The following is intentionally **not** claimed by the local reference implementation:

```text
lease consumption + arbitrary external side effect = atomic transaction
```

Achieving that property requires executor-specific semantics such as:

- durable effect identity;
- idempotency keys where supported;
- prepare/commit protocol where supported;
- external reconciliation;
- crash recovery;
- explicit handling of ambiguous outcomes.

## Budget Interaction

A reservation remains associated with the lease/effect until the outcome is settled.

A concrete executor must not release reserved resources merely because the local worker lost contact with the external effect.

`UNKNOWN` therefore requires reconciliation before final reservation settlement when the external cost/effect status cannot be determined safely.

## Revocation Interaction

Revocation prevents new authorization and may invalidate unconsumed leases according to the policy.

Revocation does not erase historical effect records.

For an already dispatched external action, the system records:

```text
REVOCATION_REQUESTED
EXTERNAL_OUTCOME_UNKNOWN
```

until reconciliation establishes the outcome.

## Safety Invariants

### E1 — Stable Effect Identity

Equivalent logical effects reuse the same durable effect identity during retry/recovery.

### E2 — No Blind Retry

`UNKNOWN` cannot transition directly to `PREPARED` for another attempt.

### E3 — Lease Binding

The effect identity is bound to the immutable execution lease.

### E4 — Reservation Conservation

Pending effects retain their resource reservations until explicitly settled.

### E5 — Durable Outcome

A resolved outcome is recorded as evidence before the effect is considered settled.

### E6 — Fail Closed on Ambiguity

Unknown authorization or unknown effect state cannot create implicit permission for another execution attempt.

## Test Matrix

| Scenario | Expected state | Retry allowed? |
|---|---|---|
| crash before prepare | AUTHORIZED / expired by policy | only with new valid authorization |
| prepare succeeds | PREPARED | yes, same effect identity |
| commit acknowledged | COMMITTED | no |
| explicit execution failure | FAILED | only under explicit retry policy |
| crash after dispatch, outcome unknown | UNKNOWN | **no blind retry** |
| revoked before execution | REVOKED / denied | no |
| duplicate effect identity | rejected | no |

## Future Executor Contract

Before any externally visible executor is introduced, it must expose a contract equivalent to:

```text
prepare(lease, effect)
→ prepared | denied

commit(effect)
→ committed | failed | unknown

reconcile(effect)
→ committed | failed | unresolved
```

`unresolved` remains non-authorizable for blind retry.
