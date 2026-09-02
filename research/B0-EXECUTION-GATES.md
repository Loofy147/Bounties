# B0 Execution Gates — 1inch Limit Order Protocol 4.3.2

**Status:** governing research gate
**Date:** 2026-09-02
**Target:** production tag `4.3.2`

This document converts the Hunter doctrine into executable gates for B0. No hypothesis becomes a security finding merely because an experiment produces an unexpected result.

## G0 — Target integrity

Record before testing:

- exact repository and production tag;
- commit/digest;
- compiler/dependency environment;
- deployment/configuration facts when relevant;
- current bounty scope;
- audit/known-issue corpus;
- timestamp and provenance.

**Pass condition:** every experiment can be reproduced against the same target identity.

## G1 — Clean baseline

Build the target without research modifications that alter production semantics.

Record:

- successful compilation;
- baseline tests;
- baseline invariant results;
- baseline transaction/state fixture hashes.

Mutation results are invalid unless this baseline is green.

## G2 — State model

Create the smallest useful executable model for each active hypothesis.

### Accounting model

Represent:

```text
order maker amount
remaining maker amount
requested making/taking amount
maker asset delta
remaining invalidation encoding
```

The model must make conservation checks explicit rather than infer them from implementation storage.

### Invalidation model

Represent:

```text
fresh
partially filled
fully filled
explicitly cancelled
bit-invalidated
epoch/series-invalidated
```

Check that no permitted transition reopens a terminal invalid state.

### Authorization model

Represent:

```text
order hash
EIP-712 domain
signer
private sender restriction
entry point
```

A positive authorization result must bind to exactly one intended domain/order context.

### Parser/extension model

Represent:

```text
packed offsets
field boundaries
args boundaries
extension binding
callback/pre/post interaction payloads
```

The test target is security-sensitive reinterpretation, not parser strictness by itself.

## G3 — Hypothesis experiments

Run H-A1 through H-D1 separately. Do not combine hypotheses until an individual experiment has a deterministic baseline.

For each experiment preserve:

1. initial state;
2. exact caller/capabilities;
3. exact call sequence;
4. block/time assumptions;
5. intermediate state transitions;
6. final state and asset deltas;
7. expected property;
8. observed property;
9. raw trace/artifacts.

## G4 — Negative controls / mutations

Each invariant needs a control that deliberately breaks the intended property.

Examples:

- bypass the remaining-amount decrement;
- alter rounding direction;
- skip an invalidation check;
- substitute an unrelated domain/order hash;
- alter one packed boundary in a controlled fixture.

The purpose is to prove that the harness would detect the relevant class of defect before real-target conclusions are drawn.

## G5 — Stateful sequence exploration

Search sequences, not isolated calls, around:

- repeated partial fills;
- full then partial attempts;
- cancellation then fill attempts;
- bit invalidation combined with epoch/series changes;
- private sender boundaries;
- signature/domain reuse;
- malformed or boundary extension layouts;
- pre/post interaction callbacks;
- rounding transitions at small and maximal values.

Use state snapshots and prefix reuse where sequence growth becomes expensive. Every candidate should be minimized before impact analysis.

## G6 — Independent validation

A candidate must be replayed through a second validation path that does not merely call the same assertion code.

Preferred order:

```text
experiment observation
→ independent invariant calculation
→ state/balance delta comparison
→ minimized replay
```

A static detector, fuzzer crash, or LLM conclusion is not independent validation.

## G7 — Scope / novelty / audit gate

Before any submission-ready classification:

```text
Reproduced
→ attacker reachable
→ security property violated
→ impact demonstrated
→ in current scope
→ not already known
→ not already covered by the relevant audit disclosure
→ minimal PoC
```

A duplicate or audited issue remains useful negative evidence but is not a new finding.

## G8 — Evidence package

The final package must link:

```text
TargetSnapshot
→ Hypothesis
→ Invariant
→ Experiment
→ Inputs/calls
→ StateBefore
→ Raw observations
→ StateAfter
→ Minimal counterexample
→ Impact proof
→ Scope proof
→ Audit comparison
→ Independent validation
```

Hash-link or content-address artifacts where practical.

## Current hypothesis order

1. H-A1 — mixed partial-fill accounting
2. H-B1 — invalidation composition bypass
3. H-C1 — authorization/domain equivalence
4. H-D1 — dynamic calldata interpretation

The order is a research priority, not an assertion that any hypothesis is vulnerable.

## Explicit boundary

Remote testing remains governed by the active bounty program. The B0 research track must not test prohibited production assets or networks. No secrets or credentials are stored in the repository.
