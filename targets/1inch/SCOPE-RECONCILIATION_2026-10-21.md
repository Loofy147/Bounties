# 1inch Scope Reconciliation — 2026-10-21

**Status:** SCOPE SNAPSHOT DISCREPANCY OPEN; no material asset-addition delta established  
**Previous records:** [`CURRENT_STATUS_2026-10-20.md`](../../CURRENT_STATUS_2026-10-20.md), [`CURRENT_STATUS_2026-09-29.md`](../../CURRENT_STATUS_2026-09-29.md)  
**Official program sources:**
- Information: https://immunefi.com/bug-bounty/1inch-SmartContracts/information/
- Scope: https://immunefi.com/bug-bounty/1inch-SmartContracts/scope/
- Release repository: https://github.com/1inch/limit-order-protocol/releases

## 1. Evidence reconciliation

The available snapshots do not support a stable, authoritative claim that the eight 1inch target rows were newly added on 14 October. Keep the discrepancy open rather than promoting one inconsistent rendering into a confirmed scope delta.

| Evidence record | What it says | Classification |
|---|---|---|
| `CURRENT_STATUS_2026-09-29.md` | Working LOP pin `4.3.4` → `7da29889efa2e635611e1caf60f85f595ff7f05f`; the live scope was checked at that time | Historical repository record |
| `CURRENT_STATUS_2026-10-20.md` | Information page update: 14 October; scope page update recorded as 14 August; eight target asset-added dates recorded as 10 June; its conclusion was that no October 14 scope addition had been established | Historical repository snapshot, not a live guarantee |
| Official search-indexed scope result checked 21 October 2026 | Scope page reports “Last Updated 20 October 2026”; all eight asset-added dates are shown as 5 October 2026 | Official source evidence, but search-indexed rather than a preserved table capture |
| Transient rendered-page attempt during this review | A render briefly returned rows with a “- new” label and an October 14 date, but this could not be reconciled consistently with the official search-indexed result and was not preserved as a stable source snapshot | Unconfirmed observation; not sufficient to establish a material change |

The eight target families in the differing views are Limit Order Protocol, Limit Order Settlement, Token-plugins, Farming Contracts, Delegating Contracts, Cross-chain Swap, Solana Crosschain, and Solana Fusion. Their names alone do not prove new source revisions or new reward eligibility.

### Decision

- **ESTABLISHED:** The saved 20 October and 29 September status records disagree with the later search-indexed scope-page values.
- **ESTABLISHED:** The official 1inch information page carries a 24-hour initial-discovery reporting rule, and the program applies only to the latest eligible tags/releases.
- **UNKNOWN:** Whether a substantive current asset addition or eligible-source change occurred that merits an alert.
- **UNKNOWN:** Whether each differing row/date reflects a real scope change, a listing/rendering inconsistency, or an update to the rendered/indexed metadata.
- **NOT ESTABLISHED:** That the eight rows were newly added on 14 October.
- **NOT ESTABLISHED:** Any vulnerability or new report eligibility from the scope discrepancy.

Therefore this is a **snapshot-quality issue, not a confirmed new opportunity**. Do not report a material scope delta until a fresh official page capture with exact row names, dates, links and source refs can be retained and reconciled against the saved snapshots.

## 2. Exact release / source gate

Existing research pin:
- Repository: https://github.com/1inch/limit-order-protocol
- Tag: `4.3.4`
- Commit: `7da29889efa2e635611e1caf60f85f595ff7f05f`

The repository warns against using default-branch/WIP code as the bounty target. Default-branch package metadata is not evidence that a corresponding eligible release tag exists. Before any future, distinct experiment, record:
1. exact live scope row and URL;
2. the repository linked from that row;
3. exact eligible tag/ref and resolved immutable commit;
4. the official evidence that this ref is eligible under the current program;
5. exact relevant audit/known-issue coverage.

If any row-to-release mapping is ambiguous, do not run a target-specific test until the program clarifies it.

## 3. H-E2 / K-04 reporting eligibility — HOLD

Prior evidence records:
- Local resolver-reward behavior: `EXPERIMENTALLY_SUPPORTED`.
- Overall H-E2 candidate: `HYPOTHESIS`.
- Bounty submission/reward eligibility: `UNKNOWN / NOT CLEARED`.

The official rule is **report within 24 hours of initial discovery**. A page-update date, asset-added date, row label, or later scope change does not reset an earlier discovery timestamp. Existing H-E2 work predates this snapshot; do not submit it unless the authorized 1inch program channel explicitly confirms its eligibility in writing.

No further synthetic version of the already-completed `C < R` H-E2 experiment is justified by a listing discrepancy. The remaining work is eligibility/audit/source reconciliation, not repeating the local mechanism.

## 4. Testing restrictions and stop rules

- Test only on a local fork under the current program rules; do not test deployed mainnet or public-testnet code.
- Do not repeat H-E2 without new evidence that changes a remaining gate.
- Do not infer an exploit from a listing, an asset-added timestamp, or a source comment.
- Do not generate or submit an AI-authored external report. Human researcher must independently validate and own any submission.
- Preserve prior labels and negative results; do not upgrade `HYPOTHESIS` to a finding from this discrepancy.

## 5. Change ledger

| Date | Observation | Decision |
|---|---|---|
| 2026-10-20 | Saved status recorded information-page update on 14 October, an older scope-page update date, and June 10 asset dates | Preserve as historical evidence |
| 2026-10-21 | Official search-indexed scope result showed a different page-update/date set (20 October / 5 October); a transient page render was inconsistent and not retained as stable row-level evidence | Keep the discrepancy OPEN; no material scope delta asserted |
| 2026-10-21 | Existing H-E2 remains beyond the documented 24-hour initial-discovery window unless the program explicitly confirms otherwise | HOLD; no repeat experiment or submission recommendation |
