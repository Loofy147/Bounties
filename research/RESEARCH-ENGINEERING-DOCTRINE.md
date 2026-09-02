# Security Research Engineering Doctrine

**Status:** Governing baseline for Hunter research
**Date:** 2026-09-02

## 1. Purpose

This document defines the method used to evolve Hunter from a hypothesis runner into an evidence-driven adversarial research laboratory.

The governing chain is:

```text
Scope
→ Target Snapshot
→ Program/State Model
→ Security Invariants
→ Hypothesis
→ Controlled Experiment
→ Independent Validation
→ Minimal Counterexample
→ Impact Proof
→ Novelty/Scope Gate
→ Evidence Bundle
→ Human Approval
```

A security claim is not established by a suspicious pattern, LLM reasoning, static warning, crash, or high test coverage alone. It requires reproducible evidence connecting attacker capability to a violated security property and demonstrated impact within the declared scope.

## 2. Target intelligence before execution

Every target begins with an immutable or version-pinned snapshot containing:

- repository/version/commit or deployment identity;
- compiler and relevant dependency versions;
- network/environment assumptions;
- current program scope;
- audit and known-issue corpus;
- deployment or configuration facts where relevant;
- timestamp and provenance.

For production bounty targets, production code must be preferred over work-in-progress branches unless the program explicitly scopes otherwise.

## 3. Model and invariant discipline

The Hunter must construct an explicit state/surface model before broad exploration.

Security invariants should be expressed independently of the exploit hypothesis. Reusable families include:

- authorization and privilege boundaries;
- asset conservation and accounting;
- nonce/invalidation monotonicity;
- signature and domain binding;
- state-machine transition validity;
- calldata/parser interpretation;
- callback and extension trust boundaries;
- stale state, ordering, race, and replay;
- upgrade/configuration boundaries;
- standard conformance properties.

Invariant libraries should be reused where applicable; target-specific invariants are added only when the protocol semantics require them.

## 4. Exploration stack

The preferred research stack is complementary:

```text
Static analysis
+
Property/stateful fuzzing
+
Coverage-guided exploration
+
Mutation testing
+
Differential/reference-model testing
+
Symbolic/constraint-guided execution
```

Tools are selected by the blind spot they close, not by popularity. A fuzzer is not a proof system, and a static detector is not an impact demonstration.

## 5. Stateful transaction-sequence discipline

Smart-contract research must treat transaction sequences and state transitions as first-class search objects. Important findings may require:

- multiple calls;
- repeated calls;
- interleavings;
- state snapshots;
- prefix reuse;
- adversarial ordering;
- boundary values and rounding;
- callback/extension interactions.

Where state-space growth becomes dominant, snapshotting, decomposition, coverage feedback, or symbolic guidance should reduce search rather than relying on unbounded sequence growth.

## 6. Mutation and negative controls

A green baseline must precede mutation scoring.

Mutation testing is used to answer:

> Can our properties detect a deliberately broken security-relevant behavior?

For each major invariant family, maintain targeted negative controls or mutants that prove the harness can distinguish valid and invalid behavior.

## 7. Differential and reference testing

Where a trustworthy semantic reference is available, compare:

```text
reference model ↔ implementation
implementation A ↔ implementation B
version N ↔ version N+1 where semantics should be preserved
```

A disagreement becomes a candidate for investigation; it is not automatically a vulnerability.

## 8. Evidence graph

A validated finding should form a traceable graph:

```text
Finding
├── TargetSnapshot
├── Hypothesis
├── Invariant
├── Experiment
├── Inputs / calls
├── StateBefore
├── StateAfter
├── Raw observations
├── Reproduction
├── Minimal Counterexample
├── Impact Proof
├── Scope Proof
├── Audit / known-issue comparison
└── Independent Validation
```

Artifacts should be content-addressed or hash-linked where practical. Rejected candidates and rejection reasons are retained to prevent repeated work and to measure false-positive pressure.

## 9. LLM role

LLMs may generate hypotheses, identify candidate invariants, propose experiment sequences, interpret traces, and prioritize search.

They do not serve as the final oracle. Execution, invariant evaluation, reproduction, impact validation, scope verification, and submission readiness must be grounded in executable evidence and independent checks.

## 10. Novelty and scope gate

Before a candidate can become submission-ready:

```text
Observed
→ Reproduced
→ Security property violated
→ Attacker controlled
→ Impact demonstrated
→ In scope
→ Not already known/audited
→ Minimal PoC
→ Independently validated
```

Failure at any gate remains a research result and should be classified rather than silently promoted to a finding.

## 11. Learning priorities

The Hunter engineering curriculum should progress through:

```text
EVM / Solidity semantics
→ state machines and invariants
→ ABI/calldata/storage
→ signatures and authorization
→ accounting/precision
→ callbacks/reentrancy/order dependence
→ static analysis and CFG/DFG
→ property/stateful fuzzing
→ mutation/differential testing
→ symbolic execution
→ transaction-sequence synthesis
→ exploit/PoC minimization
→ evidence and research automation
```

Security taxonomies should not rely on obsolete labels alone. Use living standards and repositories such as CWE, OWASP Smart Contract Security Verification Standard, EthTrust, current program rules, audit corpora, and validated public disclosures as appropriate.

## 12. Current B0 gate

For 1inch Limit Order Protocol B0, the target remains pinned to production tag `4.3.2` until the program scope says otherwise. No vulnerability is currently established.

The immediate research gate is to build an executable local harness for the hypothesis ledger and evaluate H-A1 through H-D1 with:

- clean baseline;
- target-specific invariants;
- stateful/mutation controls;
- deterministic reproduction;
- audit/known-issue comparison;
- minimized counterexample extraction.

Remote testing must remain within explicit program policy and allowlists.

## 13. Decision rule

Optimize for validated signal, not activity: precision, reproduction rate, impact accuracy, novelty, time-to-validated-finding, duplicate rate, false-positive rate, and scope-policy compliance matter more than raw hypothesis or test counts.
