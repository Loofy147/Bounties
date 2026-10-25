# Invariant Composition Benchmark v0.1

**Status:** Synthetic deterministic benchmark. No target-chain code is executed.

This standard-library Python benchmark translates three historical root-cause patterns into explicit predicates:

1. Transition postcondition / collateral-health closure (Euler-like).
2. Trusted instruction-source identity (Wormhole-like).
3. Non-negative fee domain and source-debit-to-payout reconciliation (WAX-like).

It includes three seeded defect scenarios and three clean negative controls. The fixtures are abstract state facts, not replayed exploit transactions.

## Run

From this directory, using Python 3.10+:

~~~bash
python -m unittest -v
python run_benchmark.py
~~~

The runner prints JSON and exits nonzero if a seeded defect is missed or a clean control produces a finding.

## Local verification

- Unit tests: **11 passed**.
- Seeded defect scenarios detected: **3/3**.
- Negative controls without false positives: **3/3**.

Capture the runner's current result locally with:

~~~bash
python run_benchmark.py > sample-output.json
~~~

## Interpretation limits

- This proves only that the predicates detect these supplied synthetic fixtures.
- It does not execute EVM, Solana, MoveVM, or bridge code and is not evidence of a vulnerability in a real target.
- Before applying it to an authorized target, derive the invariant from that target's specification and validate the exact release, asset model, authorization policy, scope, known issues, and permitted environment.
- The withdrawal checker assumes the principal and actual fee use the same asset, source debit equals principal plus fee, and the payout record equals principal. Separate fee assets, locks/escrows, burns, decimals, rounding, and bridge-specific liabilities require a target-specific model.
- The health checker applies only where the target specification requires a healthy post-state. It is not a universal solvency rule.
- The provenance checker does not validate signatures, message content, guardian membership, or replay protection; those are separate invariants.

## Files

- invariant_composition.py — pure, deterministic invariant predicates.
- test_invariant_composition.py — unit tests and clean controls.
- run_benchmark.py — seeded-defect and negative-control runner.
