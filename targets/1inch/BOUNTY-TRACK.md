# Bounty Track — Target Strategy Snapshot

**Snapshot:** 2026-09-02

## Objective

The immediate milestone is the first legitimate, in-scope, externally accepted paid finding. The payout amount is secondary to closing the complete external loop:

```text
scope → inspect → hypothesize → reproduce → minimize → document → submit → triage → acceptance → payment
```

## B0 — 1inch Smart Contracts

1inch is the current first reconnaissance target because it provides a concrete PoC-based external feedback loop and a published low-tier path. Before any submission or active testing, re-verify the live program page for the exact eligible release, asset, impact wording, known-issue exclusions, reporting deadline and permitted test environment.

### Candidate set

| Priority | Program | Technical fit | Public maximum at snapshot time | Immediate action |
|---|---|---:|---:|---|
| B0 | 1inch Smart Contracts | Medium | $500,000 | Pin eligible release; audit map; local-only reproduction |
| A | Cosmos | Very high | $50,000 | Scope + known-issue review |
| A- | The Graph | High | $50,000 | Graph Node/Indexer scope review |
| B | Berachain | High | $100,000 | BeaconKit/Rust protocol map |
| B | Sei | High | $500,000 | Go/Rust L1 scope review |
| B | sBTC | High | $250,000 | Bitcoin/Rust signer review |
| C | Chainlink | Medium–high | $3,000,000 | Later-stage target |

The ranking is by technical fit, reproducibility, scope clarity, evidence quality, entry barrier, competition, learning value and portfolio value; reward is deliberately last.

## B0 readiness gate

Do not submit until all are true:

- exact in-scope repository and release are pinned;
- claimed impact is explicitly in the current scope;
- known issues and prior audits are checked;
- reproduction is deterministic and local/permitted;
- minimal PoC demonstrates the effect;
- evidence is based on observed behavior, not speculation;
- submission deadline and channel are known.

## Research families

For 1inch Limit Order Protocol, preserve four invariant families:

1. Fill accounting.
2. Invalidation state transitions.
3. Authorization and domain separation.
4. Parser, extension and callback consistency.

## Important status

**No vulnerability has been established.** Existing material is reconnaissance and falsifiable hypotheses only.

## Relationship to Moirae

Moirae remains a separate protocol-verification project. Its state-machine, invariant, adversarial-schedule and minimization techniques are transferable research methods, not evidence of a vulnerability in any bounty target.
