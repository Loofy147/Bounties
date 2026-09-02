# Control Plane Durability and Recovery Contract v0.1

## Purpose

Define the minimum durability boundary required before the Control Plane can govern any external side effect.

## Durable State

At minimum, the system must durably retain:

- effect identity;
- lease identity;
- effect lifecycle state;
- policy version;
- capability identity;
- action digest;
- target identity digest;
- budget reservation/settlement state;
- monotonic sequence;
- provenance reference.

## Crash Rule

A crash may leave the system uncertain about whether an external effect occurred.

That state is represented explicitly as:

`UNKNOWN`

UNKNOWN is not equivalent to FAILED and is not retryable by default.

## Recovery Algorithm

After restart:

1. load the durable journal;
2. validate sequence monotonicity and state transitions;
3. reconstruct the latest state for each effect identity;
4. identify PREPARED/UNKNOWN effects;
5. require reconciliation before any further effect attempt;
6. resume only from an authorized and non-revoked state.

## Required Safety Property

Recovery must never transform uncertainty into permission.

Formally:

`UNKNOWN -> execution` is forbidden without an explicit reconciliation transition.

## Reservation Semantics

Budget reservation is durable before an effect reaches PREPARED.

Settlement is durable before the reservation is released.

A crash between those operations must resolve conservatively rather than create additional spend authority.

## Journal Trust Boundary

The current implementation is a local reference journal, not tamper-proof persistent infrastructure.

Before production use, the repository must define:

- durable storage guarantees;
- fsync/flush semantics appropriate to the backing store;
- corruption handling;
- snapshot/compaction semantics;
- integrity protection;
- backup/recovery behavior.

## External Side-Effect Boundary

This contract does not prove atomicity with an arbitrary remote system.

A future executor must define the protocol between:

`PEP -> executor -> external system`

including prepare/commit/reconcile semantics, stable effect identity, and unknown-outcome recovery.

## Exit Gate

Durability is not considered complete until fault-injection tests demonstrate that the following states survive restart without unsafe promotion:

- AUTHORIZED;
- PREPARED;
- FAILED;
- UNKNOWN;
- REVOKED;
- COMMITTED.
