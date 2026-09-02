# Bounty Evidence Ledger

This ledger prevents loss of work and prevents hypotheses from being mistaken for findings.

| ID | Target | Status | Evidence | Next gate |
|---|---|---|---|---|
| B0-1INCH | 1inch Limit Order Protocol | RECONNAISSANCE | pinned-release audit map and four invariant families | re-verify live scope + audits, then local reproduction |

## Preservation rule

Every significant research step should be committed to this repository with the exact target version, date, reasoning status, reproduction artifacts and outcome.

## Status transitions

```text
RECONNAISSANCE
  → HYPOTHESIS
  → REPRODUCED
  → IN-SCOPE
  → SUBMITTED
  → ACCEPTED
  → PAID
```

A negative path is also preserved:

```text
HYPOTHESIS / REPRODUCED / SUBMITTED
  → REJECTED
```

Rejected work is not deleted. Record the reason so future research does not repeat the same dead end.

## Current boundary

No submitted vulnerability is recorded here. The 1inch material remains a research dossier only.
