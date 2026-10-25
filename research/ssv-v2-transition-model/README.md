# SSV v2 transition reference model

This dependency-free Python package tests the **abstract accounting rules** used to triage SSV v2.0.0 review leads. It does not compile/execute Solidity, fork Ethereum, query live contracts, or prove a deployed implementation property.

## Run

    python -m unittest -v

Local result: **11 tests passed**.

## Covered states

- EB-aware active-cluster exposure, operator baseline counts and deviation totals.
- register → EB update → liquidate → reactivate → EB update/remove transitions.
- Retained EB snapshot semantics and final-validator cleanup after active vs already-liquidated removal.
- Shared-operator isolation between two modeled clusters.
- cSSV settlement before transfer/burn, including transferFrom allowance changes.
- Multi-hop transfer at an unchanged accumulator, immediate unstake, and dust accumulation.

## Model limitations

The model omits packed-number behavior, exact fee-index accumulation, Merkle proof validation, proxy dispatch, removed operators' full state, storage layout, EVM transaction rollback, gas, upgrade history, and the full Solidity test fixture. Passing tests prove model consistency only. Contract-level verification requires a local Hardhat fork pinned to exact current implementation hashes and a regression test in the target's own harness.
