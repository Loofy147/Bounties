# 1inch Limit Order Protocol — Local Harness Plan

**Snapshot:** 2026-09-29

## Target pin

```text
repository: https://github.com/1inch/limit-order-protocol
tag: 4.3.4
tag object: 8b8f05736b857129da3a52a37623a40af05e225d
commit: 67c56aee3b6a9f4982bf487084bd8da1f6638da0
```

The official repository states that `master` is work-in-progress and directs researchers to tagged production versions; the `4.3.2` package declares version `4.3.2` and uses Hardhat with `yarn test` / `yarn test:ci` scripts.

## Local-only setup

Run from a clean working directory:

```bash
git clone --branch 4.3.2 --depth 1 https://github.com/1inch/limit-order-protocol.git limit-order-protocol-4.3.2
cd limit-order-protocol-4.3.2

test "$(git rev-parse HEAD)" = "67c56aee3b6a9f4982bf487084bd8da1f6638da0"

# Or invoke the repository's pinned baseline runner:
# bash /path/to/Bounties/targets/1inch/tools/run-baseline.sh "$PWD"

yarn install --frozen-lockfile
yarn test:ci
```

The hash check is a hard gate. Do not substitute `master`.

## Harness layers

### L0 — Clean baseline

Run the target's existing test suite and preserve:

- node version;
- yarn version;
- dependency lockfile hash;
- test command;
- complete pass/fail result.

### L1 — State model

For each candidate order, record:

- order fields;
- maker/taker identities;
- maker/taker token balances;
- maker traits;
- order hash;
- remaining-making state;
- invalidation state;
- relevant emitted events.

### L2 — Controlled probes

Implement one test file per hypothesis family:

```text
H-A1  mixed partial-fill accounting
H-B1  invalidation composition
H-C1  authorization/domain equivalence
H-D1  dynamic calldata interpretation
```

Each test must have a fixed seed or fully enumerated boundary set. Do not use an unconstrained fuzzer as the sole evidence.

### L3 — Mutation controls

For every hypothesized invariant, create a deliberately weakened local mutant of the research model/test oracle. The harness passes only when:

1. baseline target behavior satisfies the invariant; and
2. the mutation is detected by the same test.

This separates a useful security test from a test that merely executes code.

### L4 — Minimization

When a candidate fails, minimize in this order:

```text
call count → argument count → calldata length → token/amount magnitudes → state complexity
```

Preserve the smallest deterministic reproducer.

## Evidence output

Each candidate should emit a machine-readable record with:

```text
target_commit
hypothesis_id
test_id
seed_or_case
pre_state_digest
calls
post_state_digest
observed_effect
expected_invariant
result
environment
```

## Environment constraint

A live clone/test execution was attempted from the current agent container on 2026-09-29 but failed because the execution environment could not resolve `github.com`. Therefore:

**Harness execution status: UNKNOWN / OPEN.**

This repository document is a test specification, not evidence that the suite has run successfully.

## Promotion gate

```text
baseline PASS
→ hypothesis test PASS on clean target
→ mutant KILLED
→ candidate reproducibly FAILS intended invariant
→ impact is observed
→ current scope permits that impact
→ minimized PoC
```

Only the final two gates permit movement toward `IN-SCOPE` and `SUBMITTED`.
