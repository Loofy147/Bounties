# Bounty Evidence Ledger

This ledger prevents loss of work and prevents hypotheses from being mistaken for findings.

| ID | Target | Status | Evidence | Next gate |
|---|---|---|---|---|
| B0-1INCH | 1inch Limit Order Protocol | HYPOTHESIS | Immunefi boundary re-verified 2026-09-29; tag `4.3.2` resolves through annotated tag `8b8f05736b857129da3a52a37623a40af05e225d` to commit `67c56aee3b6a9f4982bf487084bd8da1f6638da0`; four falsifiable invariant families recorded | execute clean local baseline for `4.3.4`, then run H-E1/H-E2/H-F1 alongside the original H-A1/H-B1/H-C1/H-D1 matrix with mutation controls |

## Evidence stages

```text
RECONNAISSANCE
  → HYPOTHESIS
  → REPRODUCED
  → IN-SCOPE
  → SUBMITTED
  → ACCEPTED
  → PAID
```

Negative evidence is preserved:

```text
HYPOTHESIS / REPRODUCED / SUBMITTED
  → REJECTED
```

A rejected candidate is not deleted; the reason is part of the research dataset.

## Current B0 research state

The canonical hypothesis register is `targets/1inch/HYPOTHESES.md`.

Target pin was refreshed on 2026-09-29 because tag `4.3.4` was created after the earlier `4.3.2` snapshot. `4.3.2` is not treated as the current eligible release.

Tracked families:

- H-A1: mixed partial-fill accounting;
- H-B1: invalidation composition;
- H-C1: authorization/domain equivalence;
- H-D1: dynamic calldata interpretation;
- H-E1: native-order clone / patched-hash equivalence;
- H-E2: native-order collateral / cancellation accounting;
- H-F1: Permit2Proxy authorization boundary.

No one is a confirmed vulnerability.

## Execution-state correction

The prior ledger referenced a hypothesis file that was not present in the current default-branch tree. On 2026-09-29 that inconsistency was corrected by creating the canonical register above.

A local clone/test execution was attempted on 2026-09-29 and again during the current continuation; the agent container had no DNS resolution for `github.com`. Therefore no execution result is claimed from those attempts. GitHub Actions also reported zero runs for the research branch at the time of the last check.

External audit hygiene: Immunefi states that vulnerabilities already disclosed as unpatched or unresolved in completed audits are not eligible for rewards. Audit comparison is therefore a required pre-submission gate.

## Preservation rule

Every significant research step records the exact target version, date, reasoning status, reproduction artifacts and outcome. Do not store credentials or secrets in this repository.
