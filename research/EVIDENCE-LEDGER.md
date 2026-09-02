# Bounty Evidence Ledger

This ledger prevents loss of work and prevents hypotheses from being mistaken for findings.

| ID | Target | Status | Evidence | Next gate |
|---|---|---|---|---|
| B0-1INCH | 1inch Limit Order Protocol | RECONNAISSANCE | live Immunefi scope verified 2026-09-02; production tag pinned to `4.3.2` / tag object `8b8f05736b857129da3a52a37623a40af05e225d` / commit `67c56aee3b6a9f4982bf487084bd8da1f6638da0`; official audit archive covers Limit Order Protocol v4 and v4.1 | build a local 4.3.2 harness, compare audit findings, then test invariant families |

## Verified external boundary

- Immunefi Smart Contracts program: Limit Order Protocol is explicitly in scope; the program applies only to the latest tag/releases, requires a PoC, and lists economic impacts from critical theft/freezing through lower-severity amount-delivery failures.
- 1inch repository: production guidance points researchers to tag `4.3.2` as the audited production version; `master` is explicitly WIP and not the research target.
- Official audit archive: the `Aggregation Protocol v6 and Limit Order Protocol v4` section includes OpenZeppelin audit reports for Limit Order Protocol v4 and v4.1.

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
