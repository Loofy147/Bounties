# Autonomous Security Control Plane — Architecture Decisions v0.1

## ADR-001 — Agents do not own the security boundary

**Decision:** Agent output is treated as an action proposal.

**Reason:** Model behavior is probabilistic and may be affected by ambiguity, prompt injection, tool output, or reasoning errors.

**Consequence:** Deterministic policy and enforcement must mediate execution.

## ADR-002 — The LLM Judge is advisory

**Decision:** A semantic judge can recommend ALLOW, DENY, or ESCALATE, but cannot bypass deterministic controls.

**Reason:** A model is not an appropriate sole authority for hard scope and capability constraints.

## ADR-003 — Scope is a typed authorization model

**Decision:** Scope includes more than domains and IP addresses.

It may include:

- assets;
- protocols;
- ports;
- methods;
- identities;
- time windows;
- rate limits;
- data classes;
- action classes.

**Reason:** A domain allowlist alone cannot represent many real engagement boundaries.

## ADR-004 — Findings are evidence states, not booleans

**Decision:** The system records calibrated evidence and uncertainty.

**Reason:** Replica success, model confidence, and production impact are not automatically equivalent.

## ADR-005 — Historical yield cannot determine priority alone

**Decision:** Scheduling includes a bounded exploration term.

**Reason:** Pure exploitation creates selection bias and may starve unexplored but valuable targets.

## ADR-006 — Progress is broader than graph mutation

**Decision:** Progress includes evidence gain, knowledge gain, hypothesis elimination, and state change.

**Reason:** Useful experiments may reduce uncertainty without adding graph nodes.

## ADR-007 — Budget enforcement is external

**Decision:** Monetary and computational budgets are enforced by the Governor.

**Reason:** Prompt-level budget instructions are advisory and cannot prevent runaway spend.

## ADR-008 — Fail closed

**Decision:** Uncertainty in security-critical authorization produces DENY or PAUSE, not unrestricted continuation.

**Reason:** Control-plane failure must not become a scope bypass.

## ADR-009 — No model-specific prices in architecture documents

**Decision:** Vendor/model prices and latency benchmarks belong in dated benchmark artifacts.

**Reason:** Commercial terms and model behavior change over time.

## ADR-010 — Target-specific research stays isolated

**Decision:** Control-plane research lives under `research/`; bounty-specific evidence remains under `targets/`.

**Reason:** The architecture must remain reusable across bounty programs and must not contaminate target provenance.

## ADR-011 — Controlled autonomy before production autonomy

**Decision:** Initial execution should occur against local fixtures, replicas, or explicitly controlled environments.

**Reason:** The Control Plane itself must be validated before it is trusted with higher-impact environments.

## ADR-012 — Evidence is part of execution, not a post-processing step

**Decision:** Provenance is emitted during controlled execution.

**Reason:** Retrofitting evidence after an action loses causal context and weakens reproducibility.

## Open Decisions

The following remain research questions:

- exact policy language and compiler;
- capability token format;
- storage/event model;
- scheduler algorithm;
- progress estimator;
- confidence calibration;
- formal verification boundary;
- multi-worker concurrency model;
- cryptographic provenance requirements;
- benchmark corpus design.
