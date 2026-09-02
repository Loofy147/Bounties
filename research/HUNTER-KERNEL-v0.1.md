# Evidence-Driven Bug Hunter — Kernel v0.1

**Status:** IMPLEMENTATION BASELINE
**Date:** 2026-09-02
**Repository:** `Loofy147/Bounties`

## Kernel contract

The Hunter is a bounded research engine, not an autonomous submitter.

```text
Scope Contract
→ Target Snapshot
→ Surface/State Model
→ Security Invariants
→ Hypothesis Ledger
→ Experiment Plan
→ Controlled Execution
→ Evidence Bundle
→ Independent Validation
→ Impact
→ Minimal Counterexample
→ Novelty/Scope Gate
→ Human Approval
```

## Required records

### TargetSnapshot
`target_id`, `version`, `commit_or_digest`, `environment`, `scope_snapshot`, `timestamp`, `provenance`.

### Hypothesis
`id`, `target_id`, `invariant`, `attacker_capability`, `preconditions`, `expected_violation`, `experiment`, `status`.

### EvidenceBundle
`hypothesis_id`, `inputs`, `commands_or_calls`, `pre_state`, `observations`, `post_state`, `artifact_hashes`, `reproduction`, `expected_vs_observed`.

### Validation
`real`, `reachable`, `security_property_violated`, `impact_demonstrated`, `reproducible`, `scope_confirmed`, `novelty_checked`, `reviewer`.

## Hard gates

1. No execution without an explicit scope decision.
2. No finding without raw evidence.
3. No impact claim without demonstrated effect.
4. No submission-ready state without reproducibility or an explicit characterization of nondeterminism.
5. Discovery and validation must be independently separated.
6. Rejected candidates remain stored with reasons.
7. Remote testing is bounded by program policy and target allowlists.
8. Final submission requires human confirmation.

## Benchmark ladder

`mutation → known vulnerable version → hidden seeded defect → isolated adversarial target → permitted bounty target → scale`.

Baseline must be green before mutation results are counted.

## Security invariant families

- authorization / privilege boundaries
- asset conservation / accounting
- nonce and invalidation monotonicity
- signature and domain binding
- state-machine transition validity
- parser and calldata interpretation
- callback / extension trust boundaries
- stale state, race, ordering and replay
- upgrade / configuration boundary

## Metrics

Track precision, reproduction rate, novel-find rate, impact accuracy, false-positive rate, time-to-validated-finding, cost-per-validated-finding, duplicate rate, PoC compression ratio, and scope-policy violations.

## Current application

B0 is the 1inch Limit Order Protocol research track, currently pinned to production tag `4.3.2`. The active research repository and target dossier must remain separate from Moirae.

## Operating principle

> A hypothesis is cheap. A reproducible, in-scope, evidence-backed security claim is the product.
