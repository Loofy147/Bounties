# Control Plane Next Gate v0.1 — Shared Effect Ownership

## Objective

Prove that shared workers cannot obtain concurrent effective authority for the same non-idempotent effect, and that crash recovery cannot create duplicate execution authority.

## Required model

```text
EffectKey
   ↓
Durable Effect Record
   ↓
CAS / atomic ownership claim
   ↓
Owner lease
   ↓
Execution attempt
```

## Safety properties

### C1 — Single Active Owner

For any effect identity `e`, at most one live owner may hold execution authority at a time.

### C2 — Atomic Claim

Ownership acquisition must be an atomic state transition at the durable authority. Read-then-write coordination is insufficient.

### C3 — Stale Owner Rejection

A worker holding an expired or superseded ownership token cannot execute or renew the effect.

### C4 — Duplicate Registration Prevention

Concurrent creation attempts for the same `effect_key` converge to one durable effect identity.

### C5 — Crash Recovery

A crashed owner cannot leave permanent execution authority or create a second concurrent authority during recovery.

### C6 — Revocation Interaction

Revocation must prevent new ownership claims. Existing ownership must transition according to an explicit cancellation/unknown policy.

### C7 — UNKNOWN Preservation

If ownership is lost after dispatch, recovery must preserve `UNKNOWN`; it must not infer `FAILED` and create a new effect identity.

## Required tests

1. two-worker simultaneous claim;
2. repeated claim after winning worker crashes;
3. stale token execution attempt;
4. duplicate registration race;
5. ownership renewal race;
6. revocation during ownership;
7. kill switch during ownership;
8. UNKNOWN recovery;
9. journal replay during concurrent startup;
10. budget reservation race tied to ownership.

## Exit criteria

The phase is PASS only when all tests demonstrate:

```text
one effect identity
→ one active execution owner
→ no stale-owner execution
→ crash-safe recovery
→ no budget double reservation
```

## Non-goals

This phase does not add network execution, exploit generation, adaptive scheduling, or Hunter integration.
