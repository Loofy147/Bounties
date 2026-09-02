# Bounty Evidence Ledger

This ledger prevents loss of work and prevents hypotheses from being mistaken for findings.

| ID | Target | Status | Evidence | Next gate |
|---|---|---|---|---|
| B0-1INCH | 1inch Limit Order Protocol | HYPOTHESIS | live program boundary re-verified 2026-09-02; production tag pinned to `4.3.2` / commit `67c56aee3b6a9f4982bf487084bd8da1f6638da0`; invariant ledger established; no exploit demonstrated | build executable local harness and test H-A1/H-B1/H-C1/H-D1 with mutation controls |

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

## B0 current research state

Four invariant families are explicitly tracked in `targets/1inch/HYPOTHESES.md`:

- H-A1: mixed partial-fill accounting;
- H-B1: invalidation composition;
- H-C1: authorization/domain equivalence;
- H-D1: dynamic calldata interpretation.

No one of these is a confirmed vulnerability. Parser observations, in particular, remain hypotheses until an attacker-reachable security effect is reproduced.

## Preservation rule

Every significant research step records the exact target version, date, reasoning status, reproduction artifacts and outcome. Do not store credentials or secrets in this repository.
