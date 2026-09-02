# Autonomous Security Control Plane — Invariants v0.1

## Purpose

This document defines the minimum machine-testable safety contract for the Control Plane.

The target is not a claim of absolute security. The target is a set of explicit invariants that can be implemented as deterministic tests, property tests, negative controls, and fault-injection scenarios.

## I-01 — No Direct External Action

Every externally visible action must pass through the Policy Enforcement Point.

```
external_action => enforcement_record exists
```

Negative test: remove or bypass the enforcement call and assert execution is rejected.

## I-02 — Scope Closure

A normalized destination must be within the active engagement scope.

```
normalized_target ∈ authorized_assets
```

Test families must include redirects, IPv4/IPv6, DNS changes, ports, wildcard rules, and unresolved destinations.

## I-03 — Capability Closure

An action must be covered by an unexpired capability.

```
action ∈ capability.allowed_actions
AND target ∈ capability.target_set
AND now < capability.expiry
```

## I-04 — Budget Monotonicity

Consumed budget must never decrease during an active trajectory.

```
BudgetUsed(t+1) >= BudgetUsed(t)
```

Any negative delta is an accounting integrity failure.

## I-05 — Hard Budget Ceiling

No authorized execution may cause cumulative spending to exceed the engagement ceiling.

Where provider billing data is delayed, the governor must reserve budget pessimistically rather than authorize unlimited pending spend.

## I-06 — Fail Closed

Policy, capability, or identity uncertainty must never create a fallback path to execution.

Expected behavior:

```
unknown -> DENY
timeout -> DENY
dependency failure -> DENY or PAUSE
```

## I-07 — Capability Revocation

After revocation, future requests using the revoked capability must be denied.

Previously recorded actions remain immutable evidence.

## I-08 — Temporal Scope

An action must execute inside the engagement time window.

Clock-skew policy must be explicit and conservative.

## I-09 — Approval Integrity

Actions requiring approval must contain a valid approval record bound to:

- engagement;
- action class;
- principal;
- capability;
- policy version;
- validity interval.

## I-10 — Provenance Completeness

Every security-sensitive action has sufficient metadata to reconstruct:

```
who
what
where
under which policy
under which capability
when
with what result
```

## I-11 — Parentage

Every derived action, finding, or evidence object must identify its parent trajectory or source event.

## I-12 — Idempotency

Operations with non-idempotent effects must have a stable effect identity or explicit duplicate-protection mechanism.

## I-13 — State Consistency

A recovered trajectory cannot resume from a state that is newer than its durable evidence boundary.

## I-14 — Progress Accounting

Progress cannot be defined solely as graph growth.

The implementation must permit evidence, knowledge, and hypothesis-space reduction to count as progress.

## I-15 — Risk Escalation

When an action transitions into a higher risk class, the authorization requirements must be re-evaluated before execution.

## I-16 — Evidence Before Submission

A finding cannot transition to SUBMITTED unless all mandatory evidence and human-review gates are satisfied.

## I-17 — Immutable Policy Reference

Every security-sensitive record references the exact policy version used for its authorization decision.

## I-18 — No Security Boundary on LLM Output

LLM output alone cannot authorize an action that deterministic policy and capability checks would reject.

## Verification Strategy

Each invariant should have:

1. unit tests;
2. negative controls;
3. property-based tests where useful;
4. fault injection;
5. durable evidence artifacts.

The implementation should track the invariant status as PASS, FAIL, BLOCKED, or NOT_YET_TESTED.

## Current Status

This document is a specification baseline. No invariant is considered production-proven until an executable test demonstrates it.
