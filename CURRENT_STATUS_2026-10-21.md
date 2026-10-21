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
- Scope says 14 assets total. The live extracted first page exposes 12 named addresses. The remaining two are **not inferred** and must be read from page 2 before any target is chosen.
- Program-owned repository master was observed at commit `2843ac873718e869ac138278f9f4ee3c12736544` (2026-10-14T22:14:06Z). This is a source snapshot only; it is not proof that every scoped deployment uses that exact source.
- `deployment-config/PAXGyCCIPEth.json` at that revision matches the listed PAXGy Vault, Manager, Accountant, and RolesAuthority addresses. That is useful provenance evidence, not bytecode/source equivalence proof.

### INFERENCE — fit

Transit and PAXGy map well to existing strengths:
- EIP-712 signature/domain binding and replay protection;
- cross-chain order receipt and per-order settlement state;
- value normalization across token decimals;
- vault share and fee conservation;
- privileged-role and Merkle authorization boundaries;
- deterministic local state-transition harnesses and minimal counterexamples.

### UNKNOWN / OPEN

- Exact full set of 14 scoped addresses (page 2 not captured).
- Verified-source/compiler/settings/constructor-argument/bytecode correspondence for each selected address, including proxy implementation at submission time.
- Whether the relevant source functions at master commit are identical to the scoped deployed contract source.
- Complete known-issues document and issue-by-issue audit overlap.
- A program-specific initial-discovery/report deadline was not found in the checked page content; treat the deadline as **UNKNOWN**, not absent.
- The information page prohibits testing with pricing oracles and third-party smart contracts. The scope page also contains narrower oracle-impact wording. Follow the stricter restriction until the program gives clear written clarification; no oracle/third-party interaction is authorized by this note.

### Initial implementation plan

1. Capture page 2 and record all 14 address/name/date rows.
2. For each candidate address, record chain, runtime bytecode hash at a pinned block, explorer-verified source, compiler/settings, constructor args, proxy implementation (if any), and the exact repository commit that reproduces the deployed code. Fail closed on a mismatch.
3. Read the entire linked known-issues document and map each relevant source/test path to the dated official audit reports. An inaccessible document or unread PDF is an OPEN gate, not a negative result.
4. Choose one invariant family only after steps 1–3: Transit signature/replay/settlement state or PAXGy fee/share accounting.
5. Define baseline, property, pre-state, allowed local environment, minimum impact, kill condition, evidence schema, and any required mocks before implementing a PoC.
6. Run only offline/static work until the program's restrictions and exact deployment pin permit the specific test. No production/public-testnet tests. No oracle or third-party-contract interactions without explicit authorization.
7. Keep candidate status at `RECONNAISSANCE` until deterministic observed behavior exists. No vulnerability, severity, payout, or novelty claim is made here.

## 3. Candidate ledger

| ID | Candidate family | Status | Next discriminating check | Stop condition |
|---|---|---|---|---|
| PX-TR-01 | Transit quote signature, chain/domain binding, one-use digest, cross-chain replay | `RECONNAISSANCE` | Map exact TransitStation and peer source to scoped address; audit quote hash, digest marking, peer authentication, and receipt flow | Stop if behavior is covered by audit/known issue, cannot reach in deployed config, or lacks an in-scope impact |
| PX-TR-02 | Transit amount normalization and destination amount due | `RECONNAISSANCE` | Model supported deployed token decimals and all rounding boundaries at exact deployed configuration | Do not promote dust/rounding alone; current program excludes rounding/precision loss unless a PoC demonstrates at least USD 100,000 loss |
| PX-PX-01 | PAXGy dynamic deposit/withdrawal fee and vault-share conservation | `RECONNAISSANCE` | Trace fee-module deployment, fee recipient, share-supply/NAV treatment, and deployed configuration; reconcile the relevant fee-module audits and known issues | Stop if module/behavior is out of scope, intentionally documented, or only impacts off-chain accounting not covered by the bounty |
| PX-PX-02 | PAXGy Teller / DCD supply cap and deposit slippage boundary | `RECONNAISSANCE` | Reconstruct atomic sequence: post-fee deposit, Teller mint, share transfer, total-value cap check, and rollback on revert | Stop if effect relies only on unconfigured privileged values or known operational limitations |
| PX-AUTH-01 | Merkle manager / decoder / role capability composition | `RECONNAISSANCE` | Map scoped manager and decoder bytecode + active deployed permissions; audit target/selector/argument decoding boundaries | Stop if precondition requires a privileged address/role or absent deployed Merkle/role configuration |

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
