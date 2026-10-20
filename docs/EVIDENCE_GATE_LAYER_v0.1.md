# Evidence Gate Layer v0.1

**Status:** Prototype implemented; local test suite passing.  
**Purpose:** Turn recurring bounty-research discipline into a portable, testable software layer rather than ad hoc prose.

## Design decision

Start with a small local-first evidence gate, not a smart contract and not a general autonomous pentester. A chain transaction is a poor place to store mutable scope details, sensitive evidence, private findings, or research notes. For now, version-controlled JSON plus SHA-256 evidence hashes and immutable Git revisions provide inspectable provenance. An optional external timestamp/attestation can be considered later without publishing sensitive content.

The first adapters are dependency-free Python CLIs. The record and scope-snapshot contracts are JSON so future adapters can be implemented in other languages, exposed through an API/MCP tool, backed by SQLite/Postgres, or attached to a UI without changing the evidence model.

## The record contract

- Target snapshot: program, exact asset, official scope URL, repository, immutable commit/hash, eligible-release confirmation, scope confirmation, timestamp, permitted environments, prohibited actions.
- Claim: stable ID, explicit epistemic status, falsifiable hypothesis, impact wording, first-discovery timestamp.
- Experiment: environment, scope match, destructive/public-network flags, reproducibility, PoC outcome.
- Evidence: immutable target revision, observation timestamp, artifact path or HTTPS provenance pointer, optional SHA-256, reproducibility marker.
- Program terms: PoC requirement, reporting deadline, whether that deadline was verified, target-specific AI-report policy, internal scope-refresh limit.
- Review gates: release/audit/known-issue/impact checks, independent review, human approval and human-owned submission controls.

Canonical schema: schemas/research-record-v1.schema.json. The schema is an interoperability contract; tools/bounty_gate.py adds semantic and file-system checks.

## Scope-change detection (v0.2)

The scope diff tool compares two normalized snapshots saved from official program pages. It does not fetch pages or infer terms that were not captured. Reviewers record each snapshot with a source URL, retrieval timestamp, program ID, terms, and asset IDs. The diff ignores retrieval/page-update timestamps by themselves and sorts set-like lists to avoid noisy alerts.

It reports material changes to reward ceiling/currency, KYC, initial-discovery deadline, PoC rules, AI-report policy, permitted environments, prohibited activity, disclosure/known-issue policy, asset additions/removals, asset scope status, source links, eligible release, asset-specific impacts, and asset reward data. A missing material field compared with a previously recorded value is surfaced as NOT_RECORDED rather than assumed unchanged. The output is a candidate-change ledger; a human must verify every delta against the live primary source before acting.

Run from the repository root:

    python -m tools.scope_diff examples/scope-snapshot-before.example.json examples/scope-snapshot-after.example.json --pretty

The example snapshots are synthetic fixtures and do not describe a real program.

## State discipline

The validator does not promote claims. Status changes are explicit human actions:

RECONNAISSANCE → HYPOTHESIS → REPRODUCED → IN-SCOPE → SUBMITTED → ACCEPTED → PAID

REJECTED is retained as an outcome. A reproduced local behavior is not automatically a vulnerability. A vulnerability is not automatically in scope, novel, eligible, or rewardable.

The submission_gate_pass result is only a summary of modeled internal gates. It is not an instruction to submit, a severity decision, or a guarantee of acceptance/payment. The program owner's current terms remain authoritative.

## Fail-closed checks in v0.1

- Reject a moving target ref such as main; require an immutable commit/hash.
- Require a current official scope URL and an explicit scope confirmation.
- Reject an experiment whose environment is not listed in the target contract.
- Reject public-network/destructive activity without explicit authorization; honor named prohibited activities.
- Require evidence for claims at REPRODUCED and later statuses, and bind evidence to the exact target revision.
- Constrain local artifact paths to the workspace root; require referenced files to exist; verify SHA-256 when supplied.
- Check timestamps and hard reporting deadlines when the deadline rule is confirmed.
- Block submission-gate passage if the scope snapshot exceeds the configured freshness window, release eligibility is unconfirmed, program terms are unknown, required PoC/reproduction is missing, or human review gates are incomplete.
- Enforce the program's stated AI-submission policy. Unknown policy blocks the final gate rather than being treated as permission.
- Never submit or contact a program automatically.

## Commands

Run from the repository root:

    python -m unittest discover -s tests -v
    python -m tools.bounty_gate examples/claim-record.example.json --root . --pretty
    python -m tools.bounty_gate examples/claim-record.example.json --root . --require-submission-gate

Exit codes: 0 = record valid (not necessarily submission-ready); 1 = invalid record/policy violation; 2 = input or JSON error; 3 = record valid but at least one submission gate remains blocked when --require-submission-gate is used.

The example is intentionally a HYPOTHESIS with unresolved eligibility and review gates. It is a data-shape illustration, not an actual target or finding.

## Test evidence

The unit suite covers immutable revision pinning, scope/environment refusal, destructive-action defaults, evidence presence/revision binding, SHA-256 checking, path traversal rejection, discovery deadlines, stale scope snapshots, unknown policy gates, human-review requirements, non-promotion of hypotheses, and deterministic scope-delta detection for added/removed assets, rewards, KYC, reporting deadlines, release eligibility, impacts, and test restrictions.

CI runs tests on pushes and pull requests. It does not run exploit tests against any bounty target or connect to public networks.

## Threats and limitations

This layer validates assertions in a research record; it cannot independently prove that the official scope is genuine, that the program permits every declared action, that the hypothesis is a real flaw, that the result is novel, or that impact meets a bounty tier. A mistaken researcher could incorrectly mark a Boolean true. Human review against the primary program page remains mandatory.

In v0.1, a URL is only a provenance pointer; the CLI does not fetch or authenticate remote artifacts. SHA-256 provides integrity detection only when a trusted digest is recorded. No secrets or sensitive report content should be committed to this repository.

## Evolution plan

1. v0.1 — Gate kernel: record schema, deterministic CLI, unit tests, CI.
2. v0.2 — Scope-diff utility: deterministic delta classification over manually captured snapshots. (Included in this branch.)
3. v0.3 — Official-source snapshot capture: record official page evidence and retrieval time, with human-reviewed normalized fields; do not scrape through access controls.
4. v0.4 — Evidence ledger: append-only run manifests, artifact hashes, tool versions, commit identity, controlled seeds, and killed hypotheses.
5. v0.5 — Research adapters: optional Foundry/Hardhat and generic subprocess adapters. Adapters must operate only on the declared local/permitted environment and receive no private keys by default.
6. v0.6 — Read-only interface: local dashboard/API/MCP surface for targets, claims, gates, evidence, and history.
7. Later/optional — Attestation: sign or externally timestamp digests if tamper-evidence across collaborators becomes valuable. Never put secrets, private PoCs, exploit payloads, or embargoed finding details on-chain.

## Acceptance gates for this prototype

- [x] Source is dependency-free beyond Python standard library.
- [x] Schema is versioned and portable.
- [x] Invalid scope/environment and stale/ineligible target states do not pass submission gates.
- [x] Claims are never promoted automatically.
- [x] Evidence paths are bounded to the workspace and optional hashes are verified.
- [x] Reporting deadline and AI-report policy have explicit gates.
- [x] Automated tests cover critical refusal paths.
- [x] Material scope changes are diffed deterministically from reviewed snapshots.
- [x] No bounty target was tested by this tool.
- [ ] Independent code review and mutation testing.
- [ ] Official-source snapshot capture and authentication.
- [ ] Adoption against the real Bounties records after schema migration review.
