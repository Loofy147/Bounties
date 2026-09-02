# Control Plane Next Gate v0.1 — PEP / Durable Ownership Binding

## Objective

The durable ownership and budget admission layers now provide a local transactional authority. The next unresolved safety boundary is the handoff into controlled execution admission.

The precise property is:

> An execution request that no longer owns the effect must be unable to cross the PEP/executor admission boundary.

## Required binding

The execution request must bind all of the following:

```text
effect_key
lease_id
action_digest
target_identity_digest
owner_id
fencing_token
policy_version
```

No single field is sufficient by itself.

## Safety properties

### P8 — Durable owner validation

PEP must consult the authoritative ownership record and reject a request whose owner identity or fencing token is stale, expired, revoked, or absent.

### P9 — Lease/owner consistency

A valid lease must not be usable with a different effect owner. The durable ownership record and lease must refer to the same stable `effect_key`.

### P10 — Exact request binding

PEP must reject changes to target, target-identity digest, action type/digest, policy version, lease identity, or effect identity.

### P11 — No private-state dependency

PEP must use explicit authority interfaces rather than reaching into internal dictionaries or mutable implementation state.

### P12 — Admission ordering

The controlled path must perform deterministic checks before any executor-side effect preparation.

### P13 — UNKNOWN preservation

Losing ownership after dispatch must not be translated into `FAILED`. The effect lifecycle remains `UNKNOWN` until executor-specific reconciliation resolves the external outcome.

## Critical race

The central race is:

```text
worker A          ownership authority          PEP/executor
   |                       |                       |
   | assert token T ------>|                       |
   |<------ current T -----|                       |
   |                       | token T superseded    |
   |---------------------->|------ prepare ------->|
```

A read-only ownership check cannot by itself close this race.

Therefore this phase must decide and test what the authoritative admission primitive is. A production-capable design needs either:

- an admission operation that atomically validates ownership and creates the next durable effect state; or
- an executor that honors an external fencing token as part of its authoritative commit boundary.

The local reference implementation must not claim that a separate `assert_current()` plus later execution is atomic.

## Required tests

1. current owner admitted;
2. expired owner rejected;
3. superseded fencing token rejected;
4. revoked ownership rejected;
5. lease/effect mismatch rejected;
6. action digest mismatch rejected;
7. target identity mismatch rejected;
8. policy-version mismatch rejected;
9. ownership lost between validation and admission;
10. duplicate admission for one effect rejected;
11. restart with current durable owner preserves admission rules;
12. UNKNOWN outcome remains UNKNOWN after ownership loss.

## Exit criteria

The gate is PASS only when stale ownership cannot cross the controlled admission boundary and when the race between validation and admission is represented by an explicit atomic protocol rather than an undocumented assumption.

## Non-goals

No remote target execution, exploit execution, WAF bypass, credential handling, adaptive scheduling, or Hunter integration.
