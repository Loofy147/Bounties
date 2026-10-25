# Initia MoveVM — Bounded Research Plan (No Active Exploit Testing)

**Checked:** 2026-10-25  
**Status:** Reconnaissance plan only; blocked on scope and patch provenance.

## Gate 0 — Authorization and scope (hard stop)

Before testing, obtain the current official Initia-specific disclosure/bounty terms or written authorization. Establish:

- accepted repositories/assets and exact release(s);
- whether local source-based regression tests are permitted;
- whether any isolated testnet/fork is permitted and how it is provisioned;
- reward, KYC/eligibility, PoC, initial-discovery deadline, disclosure/embargo, and known-issue rules;
- authorized intake channel and confirmation that the already-public root cause is excluded from any claim of novelty.

**Stop condition:** No explicit scope/authorization means no testing beyond reading public code and building a non-executing test specification.

## Gate 1 — Source, patch, and binary correspondence

Preserve an immutable record of:
- upstream source URL, branch/tag and commit;
- Initia's source fork and patch commit;
- Cargo/Go module references and checksums for MoveVM/compiler libraries;
- node build flags, reproducible-build output or artifact hashes when published;
- affected binary/version and fixed binary/version;
- postmortem statements tying the change to the incident.

Do not label the currently observed public heads as the vulnerable production commit merely because their dates predate the incident. Need source-to-binary correspondence.

## Gate 2 — Candidate properties (not attack scripts)

### IM-CACHE-01 — Warm/cold semantic equivalence

**Property:** For the same transaction and the same explicit state snapshot, script-cache-hit and script-cache-miss executions must yield equivalent validation decisions, state writes, events, abort status, and relevant gas behavior (allowing documented deterministic differences).

**Variant matrix:** same script bytes; different sender/signers; different type arguments and argument bytes; changed module/storage state; transaction/session boundary; valid and invalid authorization contexts. These are test dimensions, not a claim about the exact historical cache key or exploit path.

**Failure evidence:** A cache hit changes the authorization/validation result or state effect relative to a clean cache for the same input context, or state/context from one transaction leaks into another.

### IM-ACCOUNT-01 — Authorized state-write provenance

**Property:** A user balance increase must be explainable by an authorized resource mutation path, such as a valid mint, transfer from a source balance, protocol-authorized bridge mint, genesis/migration operation, or another documented rule.

Do not assume a universal `sum(user balances) = total_supply` equation without reading the actual token/resource model. For each asset, document the supply counter, balances, reserves/escrows, burn paths, and system-account balances; then state the correct conservation relation.

**Failure evidence:** A successful execution increases an account's spendable balance with no corresponding authorized state transition or permitted accounting source, or creates a mismatch in the asset's documented conservation relation.

### IM-BRIDGE-01 — Backing and redemption consistency

**Property:** An external reserve release must be justified by the exact authorized cross-domain evidence expected by that bridge adapter (burn/redeem state, message provenance, amount, asset identity, destination, nonce/replay protection, and any required finality proofs).

**Failure evidence:** A fabricated/unbacked balance can trigger a legitimate redemption route without the bridge's expected backing/accounting precondition. The known incident itself is already public and is not a novel candidate.

## Gate 3 — Regression test construction

Only after Gates 0 and 1 close:
1. Build isolated local tests against the exact approved pre-fix and fixed commits.
2. Prove the pre-fix baseline is reproducible only from source and fixtures; do not use live production.
3. Add one property per test; keep VM cache tests separate from asset-accounting and bridge tests.
4. Add clean-cache/warm-cache, valid/invalid signer, authorized/unauthorized state-write, mint/burn and backing positive/negative controls.
5. Introduce test-only oracle mutations to show the test detects the weakened property.
6. Compare fixed and pre-fix behavior, then independently rerun from a clean checkout.
7. Preserve logs, build hashes, state diffs, test seed/case, exact command, and raw evidence.
8. Review the public patch/postmortem and known issues before promoting any distinct new candidate.

No test here is executed by this document.

## Gate 4 — Runtime monitoring design

Prefer **provenance-aware state-transition monitoring** over watching only `Mint` events:

- Instrument MoveVM/adapter-level state writes to relevant coin/fungible-asset resources.
- Attribute each positive balance delta to a transaction, call path, module/function, and authorized operation class.
- Reconcile asset-specific account balances, supply counters, system/bridge escrow, burns, and mint authorities according to that asset's actual accounting model.
- Correlate source-chain burn/redemption evidence with destination-chain reserve releases.
- Emit an alert for an unexplained spendable-balance increase, a write path lacking authorized provenance, inconsistent supply/accounting deltas, duplicate/replayed redemption evidence, or cache-dependent semantic differences.
- Record pre/post state hashes and evidence IDs; require independent confirmation before treating an alert as a vulnerability.

A generic balance-total equation is not sufficient for all asset frameworks. Burned reserves, unclaimed balances, resource accounts, bridges, and supply counters must be modeled explicitly.

## Threat taxonomy (descriptive only)

MITRE AADAPT mappings are broad behavioral labels, not root-cause proof:
- **ADT3016 — Generate Counterfeit Tokens:** the unbacked-value effect.
- **ADT3012 — Exploit Smart Contract Implementation:** if a software implementation flaw is confirmed to be the cause.
- **ADT3007 — Exploit Consensus Logic:** **not assigned on current evidence**; a MoveVM execution bug does not by itself establish a consensus fault.

References: [AADAPT techniques](https://aadapt.mitre.org/techniques/), [ADT3016](https://aadapt.mitre.org/techniques/ADT3016/), [ADT3012](https://aadapt.mitre.org/techniques/ADT3012/), [ADT3007](https://aadapt.mitre.org/techniques/ADT3007/).

## Decision

**Current status:** RECONNAISSANCE / KNOWN PUBLIC INCIDENT.  
**Do not:** report the existing incident as novel, assume bounty terms, run an exploit against live systems, or claim a specific cache implementation flaw before the postmortem/patch establishes it.  
**Next action:** obtain official scope and the post-incident patch/build mapping. Until then, keep this as a method and regression-test plan, not an active exploit campaign.
