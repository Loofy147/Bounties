# Control Plane Kernel v0.1

This package is a **local-only reference implementation** of the policy-bounded control-plane primitives defined in `research/CONTROL-PLANE-ARCHITECTURE-v0.1.md`.

## Included

- deterministic engagement-policy checks;
- scoped capabilities;
- immutable execution leases;
- pessimistic budget reservations;
- capability revocation;
- independent engagement kill switch;
- duplicate effect identity protection;
- trajectory registration;
- hash-linked provenance.

## Explicit non-goals

The kernel does not perform network requests, exploit execution, target discovery, or payload generation. It is a control and accounting reference for local tests.

## Trust boundary

The kernel models the expected order:

```text
Action proposal
    ↓
Policy + capability decision
    ↓
Budget reservation
    ↓
Immutable execution lease
    ↓
PEP consumption point
    ↓
Evidence/provenance
```

The next implementation increment should add a real local PEP adapter, target-identity binding, durable revocation, isolation profiles, approval binding, and concurrency/property tests before any target integration.
