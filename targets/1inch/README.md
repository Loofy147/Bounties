# B0 — 1inch Limit Order Protocol

**Status:** RECONNAISSANCE / HYPOTHESIS — no vulnerability established.

## Eligibility boundary

The 1inch Smart Contracts program was re-verified on 2026-09-02. Official Immunefi scope states that Limit Order Protocol is in scope, applies only to the latest tag/releases, requires a PoC, and prohibits testing on mainnet/public testnets; testing must use local forks.

The production source guidance currently identifies tag `4.3.2` as the latest production/audited version and warns that `master` is work-in-progress. Verify again immediately before any submission.

```text
repository: 1inch/limit-order-protocol
tag: 4.3.2
rule: never treat master/WIP as the bounty target
research environment: local fork only
scope source: Immunefi 1inch Smart Contracts program, verified 2026-09-02
production source: 1inch/limit-order-protocol README, verified 2026-09-02
```

The program currently lists critical, high, medium, and low smart-contract impacts and requires reproducible impact evidence. See the live Immunefi program page before submission.

## Primary audit surface

### A — Fill accounting

Study `fillOrder`, `fillOrderArgs`, `_fillOrder`, remaining-making-amount checks, and invalidator updates.

Invariant A1: cumulative maker-side outflow cannot exceed the order's encoded making amount, and repeated/partial/mixed fill sequences preserve the intended remaining amount state.

### B — Invalidation

Study `cancelOrder`, `cancelOrders`, `bitsInvalidateForOrder`, remaining invalidation and epoch/series interactions.

Invariants B1/B2: invalidated orders cannot be filled afterwards; different invalidation mechanisms cannot bypass or corrupt one another.

### C — Authorization and domain separation

Study `hashOrder`, domain separator construction, signature verification, allowed-sender/private-order enforcement and first-fill/replay transitions.

Invariants C1/C2: signatures remain bound to intended order/domain context, and private-order sender restrictions remain enforced across entry points.

### D — Parser, extensions and callbacks

Study `isValidExtension`, predicates, `_parseArgs`, pre/post interactions, taker interactions and token-transfer suffix parsing.

Invariants D1/D2: calldata slicing cannot reinterpret security-sensitive fields; callbacks cannot invalidate accounting, authorization or cancellation assumptions.

## Experiment order

```text
pin exact release
→ clean baseline
→ one-order state model
→ accounting boundaries
→ invalidation transitions
→ authorization/domain transitions
→ parser/callback boundaries
→ seeded fuzzing
→ scope + audit comparison
→ minimized PoC
→ submission only after all gates pass
```

## Stop conditions

Stop when the target is out of scope, the effect is theoretical, the issue is already known/audited, reproduction is nondeterministic, or the demonstrated issue is only stylistic/best-practice.

## Evidence package

Every serious candidate should preserve:

- exact repo/tag/commit;
- contract and function path;
- intended invariant;
- minimal pre-state;
- exact call/transaction sequence;
- observed post-state;
- deterministic PoC;
- impact calculation tied to program wording;
- audit/known-issue comparison;
- scope eligibility evidence.
