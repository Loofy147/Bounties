# Opportunity Follow-up — 2026-10-21

**Status:** SOURCE REVIEW RECORDED; technical candidates remain gated  
**Repository:** `Loofy147/Bounties`  
**Base main commit observed before this follow-up:** `bbf4a323543462b6a71626d2b281246870d9b842`  
**Checked:** 2026-10-21 (official program pages and program-owned repository)

## Executive decision

1. **Keep the 1inch scope discrepancy OPEN.** The official search-indexed scope result reports last updated 2026-10-20 and eight asset-added dates of 5 October 2026, while the earlier local snapshot records June 10 and a prior scope-page update of August 14. The prior material does not justify asserting an October 14 asset addition. Preserve the historical snapshot and use [`targets/1inch/SCOPE-RECONCILIATION_2026-10-21.md`](targets/1inch/SCOPE-RECONCILIATION_2026-10-21.md) as the unresolved discrepancy record.
2. **Prioritize Paxos Labs for bounded source-level reconnaissance.** Its official search-indexed information and scope pages show last updated 2026-10-20; the program went live 2026-10-20. The work matches existing Solidity, authorization, accounting, order-state, and deterministic-harness capabilities. Do not start a target-interacting PoC until source-to-deployment, known-issue, and testing-policy gates are cleared. See [`targets/paxos-labs/README.md`](targets/paxos-labs/README.md).
3. **Keep 1inch H-E2 on HOLD.** Local mechanism remains `EXPERIMENTALLY_SUPPORTED`, but the overall candidate remains `HYPOTHESIS` and reporting eligibility is `UNKNOWN / NOT CLEARED`. The 24-hour timer runs from initial discovery, not from a scope-page change. Do not repeat the already-completed synthetic experiment and do not submit without explicit program eligibility confirmation.
4. **No vulnerability is established by this follow-up.** No new target-interacting tests were run and no external report was prepared or submitted.

## 1. 1inch — verified scope correction

Official sources:
- Information: https://immunefi.com/bug-bounty/1inch-SmartContracts/information/
- Scope: https://immunefi.com/bug-bounty/1inch-SmartContracts/scope/
- Release source: https://github.com/1inch/limit-order-protocol/releases
- Detailed reconciliation: [`targets/1inch/SCOPE-RECONCILIATION_2026-10-21.md`](targets/1inch/SCOPE-RECONCILIATION_2026-10-21.md)

### ESTABLISHED / OPEN

- **ESTABLISHED:** Official 1inch program information states a 24-hour initial-discovery reporting rule.
- **ESTABLISHED:** The previous status snapshot recorded eight asset dates of 2026-06-10 and a scope-page update of 2026-08-14.
- **ESTABLISHED:** The current official search-indexed scope result reports a 2026-10-20 page update and eight asset-added dates of 2026-10-05.
- **OPEN:** This is a discrepancy requiring row-by-row recheck of the live official page. Do not label it an October 14 addition or material asset addition without direct supporting evidence.
- **UNKNOWN:** Whether the scope display maps each row to a new eligible release/commit.

Do not treat the page update or asset-added date as a reset of H-E2's initial-discovery clock. Preserve H-E2's existing status and do not repeat the completed synthetic experiment.

## 2. Paxos Labs — serious follow-up, reconnaissance only

Official sources:
- Information: https://immunefi.com/bug-bounty/paxos-labs/information/
- Scope: https://immunefi.com/bug-bounty/paxos-labs/scope/
- Resources: https://immunefi.com/bug-bounty/paxos-labs/resources/
- Program-owned repository: https://github.com/paxoslabs/pxl-boring-vault
- Dossier and gates: [`targets/paxos-labs/README.md`](targets/paxos-labs/README.md)

### ESTABLISHED

- Program live since **2026-10-20**; official information and scope pages were observed as last updated **2026-10-21**.
- Maximum reward: **$500,000**; payout currency USDG on Ethereum.
- Critical: 10% of directly affected funds, minimum $10,000 and maximum $500,000.
- High: $5,000–$10,000. Medium: $1,000 flat.
- KYC required; PoC required for every severity; Responsible Publication Category 3 requires approval.
- Scope says 14 assets total. The live scope UI was paginated and all 14 rows are now captured, including PAXGy WithdrawQueue and its fee module on page 2. All rows display 5 October 2026 as their asset-added date.
- Program-owned repository master was observed at commit `2843ac873718e869ac138278f9f4ee3c12736544` (2026-10-14T22:14:06Z). This is a source snapshot only; it is not proof that every scoped deployment uses that exact source.
- `deployment-config/PAXGyCCIPEth.json` at that revision matches the listed PAXGy Vault, Manager, Accountant, and RolesAuthority addresses, but its Teller address is zero and therefore does not pin the scoped Teller. This is config provenance, not proof of complete deployment equivalence.
- TransitStation at `0x49AAA...D7d28` is explorer-verified exact match / Sourcify `exact_match`, Solidity 0.8.21, optimizer 200, Shanghai. The normalized source comparator confirms equality after changing only the three-character NatSpec phrase discrepancy; raw text is not byte-identical and the runtime compilation/build pin remains open.
- Added the offline utility [`tools/source_pin/compare_verified_source.py`](tools/source_pin/compare_verified_source.py), with nine passing unit tests. It distinguishes exact text matches from comment/whitespace-only differences and fails closed on every non-exact source pin.
- DCD fee module at `0x6E0A...B8c6D` is Etherscan Exact Match, and verified source text equals the pinned `src/helper/DCDAssetSpecificFeeModule.sol` at commit `2843ac8...` exactly.
- Etherscan marks the scoped Accountant, WithdrawQueue, and WithdrawQueue fee module as Similar Match; their source drift is not resolved. Do not target those contracts until the diff is reconciled.

### INFERENCE — fit

Transit and PAXGy map well to existing strengths:
- EIP-712 signature/domain binding and replay protection;
- cross-chain order receipt and per-order settlement state;
- value normalization across token decimals;
- vault share and fee conservation;
- privileged-role and Merkle authorization boundaries;
- deterministic local state-transition harnesses and minimal counterexamples.

### UNKNOWN / OPEN

- Exact source equivalence remains open for the Accountant, WithdrawQueue, WithdrawQueue fee module, DCD, manager/decoder/authority and other candidates except the DCD file's verified source text match.
- The official known-issues Google Doc body was directly extracted and reviewed on 2026-10-21; documented behaviors are now listed as killed/known in `targets/paxos-labs/AUDIT-AND-KNOWN-ISSUES_2026-10-21.md`.
- TransitStation Pashov, Guardian, yAudit reports and PAXGy fee-module Pashov/yAudit reports were text-extracted and candidate titles/statuses reconciled. The reports use historical commits and were not fully visually inspected; a known finding remains prior art even if its original audit commit differs.
- Exact current deployed configuration/state (roles, peers, fee map, queue params, implementation addresses and runtime code hashes at a pinned block) remains open.
- A program-specific initial-discovery/report deadline was not found in the checked page content; treat the deadline as **UNKNOWN**, not absent.
- The information page prohibits testing with pricing oracles and third-party smart contracts. The scope page also contains narrower oracle-impact wording. Follow the stricter restriction until the program gives clear written clarification; no oracle/third-party interaction is authorized by this note.

### Work completed and next gate

1. ✅ Captured all 14 official scope rows and dates.
2. ✅ Read the official known-issues document body directly and mapped exclusions.
3. ✅ Text-extracted key Transit and PAXGy fee-module audit reports and recorded known/resolved/acknowledged findings.
4. ✅ Retrieved Sourcify source for TransitStation and DCDAssetSpecificFeeModule. DCD source matches the pinned repo file exactly. TransitStation matches after one NatSpec phrase normalization; direct line diff against the Pashov follow-up source has only the `OrderSubmitted` event signature/emission shape and that comment phrase changed, with no other file-body differences.
5. ✅ Recorded non-exact Explorer source matches for Accountant, WithdrawQueue, and WithdrawQueue fee module; these remain blocked pending semantic source-diff reconciliation.
6. ✅ Added and tested the offline fail-closed source comparator (9/9 unit tests passed).
7. ⏳ Next: close remaining selected-target deployment/build/config pins before considering any new hypothesis. Current decision: no candidate clears the serious-work gate, so no PoC is justified yet.

All work so far is static/source/audit review. No target-interacting PoC was run. No vulnerability, severity, payout or novelty claim is made.

## 3. Candidate ledger

| ID | Candidate family | Status | Decision |
|---|---|---|---|
| PX-TR-01 | Transit quote signature, chain/domain binding, one-use digest, cross-chain replay | `RECONNAISSANCE / BLOCKED` | Core current source matches the Pashov follow-up source except for event log ABI/payload and comment. Related state-transition failures are already known/fixed/acknowledged; no distinct target hypothesis survives. Do not start a PoC. |
| PX-TR-02 | Cross-chain decimal normalization / dust / zero `amountDue` | `KILLED / KNOWN AUDIT ISSUE` | yAudit, Guardian and Pashov record adjacent dust/low-decimal fee behaviors; no repeat. |
| PX-TR-03 | Version-skewed payload, receive-route/backlog, peer removal | `KILLED / ACKNOWLEDGED AUDIT ISSUE` | Guardian/yAudit record the behavior; do not repackage. |
| PX-PX-01 | DCD fee arithmetic and per-token fee configuration | `RECONNAISSANCE / CONFIGURATION GATE OPEN` | Deployed module source matches repo, but owner/fee mapping/config and qualifying unprivileged impact are not established. |
| PX-PX-02 | Cross-chain DCD supply cap | `KILLED / KNOWN ISSUE` | Explicit official issue; do not repeat. |
| PX-PX-03 | Dynamic PAXGy fee/oracle/share accounting | `BLOCKED / SCOPE MAPPING OPEN` | Dynamic modules are not the scoped DCD fee contract; oracle testing is restricted and audit overlap exists. |
| PX-WQ-01 | WithdrawQueue refund recipient, receipt screening, raw-hash signatures | `KILLED / KNOWN ISSUE` | Explicit official issue and source Similar Match not resolved. |
| PX-WQ-02 | Queue processor gas/refunds and shared CCIP rate limits | `KILLED / KNOWN ISSUE` | Explicit known issues, not a new theft candidate. |
| PX-AUTH-01 | Merkle double-preimage / decoder authorization | `KILLED / KNOWN ISSUE / DESIGN-BOUNDED` | Official known-issues document says no viable double-preimage route and describes decoder behavior as bounded. |
| PX-EE-01 | EquivalentExchange flash-loan/dangling approvals | `REPORTED / FOLLOW-UP FIX MERGED` | PR #342 merged 2026-09-08; EquivalentExchange UManager is not a separately listed target address. |

These IDs label investigation lines, not vulnerability reports. No candidate is `HYPOTHESIS`, `REPRODUCED`, or `IN-SCOPE` yet.

## 4. Policy and evidence gates

- Do not infer a vulnerability from an opportunity listing or source comments.
- Keep claims labelled `ESTABLISHED`, `EXPERIMENTALLY_SUPPORTED`, `INFERENCE`, `HYPOTHESIS`, or `UNKNOWN`.
- Keep failed/killed hypotheses and reasons in the record.
- Do not repeat H-E2's completed synthetic experiment without genuinely new evidence that changes an open gate.
- Do not submit an AI-generated report. The human researcher must independently verify and own any external submission.
- If the current program's allowed testing boundary is ambiguous, use static/source review only until clarification arrives.
- Report future opportunity runs as delta-only: new program/target or material term change, with a dated prior snapshot and official source evidence.

## Source register checked 2026-10-21

- 1inch Immunefi information/scope pages listed above.
- Paxos Labs Immunefi information/scope/resources pages listed above.
- https://github.com/paxoslabs/pxl-boring-vault/commit/2843ac873718e869ac138278f9f4ee3c12736544
- https://github.com/paxoslabs/pxl-boring-vault/blob/master/deployment-config/PAXGyCCIPEth.json
- https://github.com/paxoslabs/pxl-boring-vault/blob/master/src/transit/TransitStation.sol
- https://github.com/paxoslabs/pxl-boring-vault/blob/master/src/helper/DistributorCodeDepositor.sol
- https://github.com/paxoslabs/pxl-boring-vault/blob/master/src/helper/PaxgyDynamicDepositFeeModule.sol
- https://github.com/paxoslabs/pxl-boring-vault/blob/master/src/helper/PaxgyDynamicWithdrawalFeeModule.sol
- https://github.com/paxoslabs/pxl-boring-vault/blob/master/src/base/Roles/AccountantWithRateProviders.sol
- https://github.com/paxoslabs/pxl-boring-vault/tree/master/audit
