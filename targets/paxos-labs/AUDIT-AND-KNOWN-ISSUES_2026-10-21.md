# Paxos Labs — Audit and Source-Pin Reconciliation

**Checked:** 2026-10-21  
**Repository snapshot:** `paxoslabs/pxl-boring-vault` commit [`2843ac873718e869ac138278f9f4ee3c12736544`](https://github.com/paxoslabs/pxl-boring-vault/commit/2843ac873718e869ac138278f9f4ee3c12736544)  
**Use:** prevent known-issue duplication and select a candidate only after source-to-deployment gates pass. This is research triage, not a vulnerability report.

## 1. Scope inventory — 14/14 captured

Official scope: https://immunefi.com/bug-bounty/paxos-labs/scope/

All listed rows show **Added on: 5 October 2026**. Scope is by deployed address; a listed proxy's implementation at report time is also in scope.

| # | Target | Ethereum address | Source / status at this check |
|---:|---|---|---|
| 1 | TransitStation | `0x49AAA987b1a7e9E4AE091dcD8332c39F322D7d28` | Etherscan/Sourcify exact-match classification; text reconciliation has one NatSpec discrepancy still to normalize |
| 2 | Transit BoringVault | `0x91FE06C6E9F97E7DE4580A280E03046155f8e1e3` | Sourcify record found; exact source/commit map not closed |
| 3 | Transit Manager | `0x666156ab52bb9984F5c3985726f048Dd4A73887a` | Sourcify API returned 404 at this check; source map open |
| 4 | Transit RolesAuthority | `0x3B4decc43d2173280198B46532Ef570062FCc8f5` | Verified metadata returned, Solidity 0.8.20, optimizer 200, Shanghai; exact source map open |
| 5 | Transit Decoder | `0xF34942E8612ccE476307B30a6246B43ce42B5D20` | Verified metadata returned, Solidity 0.8.21, optimizer 200, Shanghai; exact source map open |
| 6 | PAXGy Token BoringVault | `0x6c6494Fd9962eB98B94ffA48F6679058F820700e` | Sourcify record found; exact source/commit map open |
| 7 | PAXGy Manager | `0x353741aBa79974a90F88594f6CBd1a9c54651015` | Sourcify record found; exact source/commit map open |
| 8 | PAXGy Accountant | `0x397e38359f169748a02bc11f98D4f451FE88C1fd` | Etherscan says Similar Match; do not substitute repository HEAD |
| 9 | PAXGy Teller | `0x41AB5d8387e60E30AACCF11357C306f6d875A6f7` | Sourcify record found; exact source/commit map open |
| 10 | PAXGy Roles Authority | `0xC444dA4DF6AF6A9A3891a720c1712a4188d899DD` | Verified metadata returned, Solidity 0.8.20, optimizer 200, Shanghai; exact source map open |
| 11 | PAXGy DistributorCodeDepositor | `0xF6dE922D08cF9Ee4e7cE25ca1f3936EC1AA1f62C` | Exact metadata query rate-limited; source map open |
| 12 | PAXGy DCD FeeModule | `0x6E0A209672f6e357B2B5435AB6AEa2acbB4B8c6D` | Etherscan Exact Match; Sourcify source text equals repo file at the pinned commit |
| 13 | PAXGy WithdrawQueue | `0x69e0BF658bE5600864A946b4e5B911736D248FB4` | Etherscan says Similar Match; source drift must be reconciled |
| 14 | PAXGy WithdrawQueue Fee Module | `0xF41e79D6e646f334C2fc4ea5Ae609707AE82264D` | Etherscan says Similar Match; source drift must be reconciled |

Official page-2 rows captured using the live Immunefi pagination control:
- [PAXGy WithdrawQueue](https://etherscan.io/address/0x69e0BF658bE5600864A946b4e5B911736D248FB4#code), “Facilitates user withdrawals.”
- [PAXGy WithdrawQueue Fee Module](https://etherscan.io/address/0xF41e79D6e646f334C2fc4ea5Ae609707AE82264D#code), “Determines withdrawal fees.”

The total inventory is now closed (14/14). This does **not** close per-address code eligibility.

## 2. Deployed source and compiler evidence

### 2.1 TransitStation

- Scoped address: [`0x49AAA987b1a7e9E4AE091dcD8332c39F322D7d28`](https://etherscan.io/address/0x49AAA987b1a7e9E4AE091dcD8332c39F322D7d28#code)
- Etherscan reports **Source Code Verified (Exact Match)**.
- Sourcify API v2 reported `match = exact_match`.
- Compiler: `0.8.21+commit.d9974bed`; optimizer enabled, 200 runs; EVM `shanghai`.
- The verified source file is `src/transit/TransitStation.sol`.
- Program-owned pinned file at commit `2843ac873718e869ac138278f9f4ee3c12736544` has Git blob SHA `d83ef26ca09749a8503c9447d586449d45d46261`.
- Full source text comparison found a first discrepancy in NatSpec around `forceSetUsedDigestTrue`: deployed verified text says “block it from ever **becoming** received”; the pinned GitHub file says “block it from ever **being** received”. Lengths differ by 3 characters. The normalized comparison was rerun: replacing only the phrase “becoming received” with “being received” makes the full file text exactly equal. Raw source text is **not** byte-identical. The difference is confined to NatSpec, but comments can change compiler metadata, so this is not proof of identical runtime bytecode. Full compilation/dependency/constructor/immutable reconstruction remains open.
- Source/compiler identification is substantially stronger than a package version, but the chain/block bytecode hash and constructor/immutable configuration still need an evidence bundle before a PoC.

### 2.2 DistributorCodeDepositor fee module (correct source identification)

- Scoped address: [`0x6E0A209672f6e357B2B5435AB6AEa2acbB4B8c6D`](https://etherscan.io/address/0x6E0A209672f6e357B2B5435AB6AEa2acbB4B8c6D#code)
- Etherscan reports **Exact Match**, name `DCDAssetSpecificFeeModule`, compiler `0.8.21+commit.d9974bed`, optimizer 200, EVM Shanghai.
- Sourcify verified source text matched exactly with the pinned repository file:
  - Path: `src/helper/DCDAssetSpecificFeeModule.sol`
  - Commit: `2843ac873718e869ac138278f9f4ee3c12736544`
  - Git blob SHA: `f79f17a6a45724598f061488b8eccb053a41c398`
- This is **not** the same contract as `PaxgyDynamicDepositFeeModule`. Do not infer that a dynamic oracle fee module is deployed at this scope address.

### 2.3 Non-exact or unresolved mappings

| Address / target | Current observation | Gate before testing |
|---|---|---|
| PAXGy Accountant | Etherscan Similar Match to a different source address; compiler/settings visible | Obtain full verified source and compare code/immutables against repo blob `35c34e1d2c01b648a1dc07ca9576101a1dc5987f`; reconcile the similar-match diff |
| PAXGy WithdrawQueue | Etherscan Similar Match, compiler `0.8.21`, optimizer 200, Shanghai | Compare deployed `WithdrawQueue` source to repo blob `f0b60a43f77567481d2d907e75b7bfee90e81a8d`; resolve all semantic diffs |
| PAXGy WithdrawQueue Fee Module | Etherscan Similar Match, compiler `0.8.21`, optimizer 200, Shanghai | Compare deployed module to repo blob `0d4530eb300908f99abb08c09a2142193b72e20e`; resolve all semantic diffs |
| PAXGy DistributorCodeDepositor | Sourcify request hit service rate limit before a result | Retry when service allows, then compare verified source, config, and blob `68521bf60f46bb4052543780d58c7b3b9270fdf0` |
| Remaining manager/decoder/vault/teller/authority entries | Some Sourcify metadata records exist; exactness and repo equivalence are not established consistently | Record runtime bytecode hashes, compiler metadata, constructor args, source paths and resolved diffs for the chosen target |

Public-source links:
- [TransitStation at the pinned source commit](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/transit/TransitStation.sol)
- [DCDAssetSpecificFeeModule at the pinned source commit](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/helper/DCDAssetSpecificFeeModule.sol)
- [Sourcify v2 — TransitStation source/metadata](https://sourcify.dev/server/v2/contract/1/0x49AAA987b1a7e9E4AE091dcD8332c39F322D7d28?fields=sources,metadata)
- [Sourcify v2 — DCD fee module source/metadata](https://sourcify.dev/server/v2/contract/1/0x6E0A209672f6e357B2B5435AB6AEa2acbB4B8c6D?fields=sources,metadata)

## 3. Official known-issues register read directly

Primary document: [Transit/PAXGy Immunefi Known Issues](https://docs.google.com/document/d/14gImubrl0MNn_Jl_2_jCW1QPD4ra_MqYX-TV8S7JGlQ/edit). The document body was successfully extracted and reviewed on 2026-10-21. The earlier statement that this document was inaccessible is superseded.

### 3.1 PAXGy and WithdrawQueue — do not re-test these listed behaviors

| Known behavior | Official status/description | Research disposition |
|---|---|---|
| DCD supply cap is single-chain only; cross-chain bridging can let aggregate supply exceed a per-chain cap | Explicitly documented | `KILLED / KNOWN ISSUE`; no repeat experiment |
| `shareLockPeriod` / `shareUnlockTime` do not restrict share transfer, bridging or withdrawals; lock only bounds `refundDeposit` | Explicitly documented | `KILLED / KNOWN ISSUE` |
| WithdrawQueue `refundReceiver` stays fixed at submission while the receipt NFT can be transferred; refunds go to original receiver | Explicitly documented | `KILLED / KNOWN ISSUE` |
| WithdrawQueue receipt NFT transferable without Predicate/KYT screening | Explicitly documented; Predicate screening applies to DCD deposits, not withdrawal path | `KILLED / KNOWN ISSUE` |
| WithdrawQueue signatures use raw keccak digest rather than EIP-712 | Explicitly documented; replay protections include chainId, queue address, deadline, and submission nonce where applicable | `KILLED / KNOWN ISSUE` |
| Processor can cause a selected order to be refunded by limiting gas in a `bulkWithdraw` try/catch | Explicitly documented; funds are refunded, and only processor role can do it | `KILLED / KNOWN ISSUE`; privileged/liveness path |
| CCIP lane rate limits shared across users can be intentionally consumed, temporarily blocking bridges; in-flight messages are retryable | Explicitly documented; no funds at risk | `KILLED / KNOWN ISSUE`; not a theft hypothesis |
| ManagerWithMerkleVerification double-preimage theory | Document says no viable attack vector due to required code at hash-derived address and privileged root/proof roles | `KILLED / KNOWN ISSUE` |
| Trusted owner, strategist, exchange-rate, queue-processor, pauser and freeze-manager powers | Explicit trust assumptions, with queue processor trusted for liveness | Do not repackage privileged-role misuse |

### 3.2 Transit — do not re-test these listed behaviors

| Known behavior | Audit / official status | Research disposition |
|---|---|---|
| Transit deployment lacks cross-chain protection salt / deployer-key protection | Explicitly listed in known issues | `KILLED / KNOWN ISSUE`; do not test malicious deployment/phishing |
| `executePendingOrders` decoder intentionally does not sanitize nested fields; fills remain bounded to pending orders, fixed receivers, `amountDue`, vault approvals and residual-allowance check | Explicitly documented as bounded design | `KILLED / KNOWN ISSUE` |
| Pausing does not prevent already-bridged orders being queued; receive path intentionally ignores pause | Explicitly documented | `KILLED / KNOWN ISSUE` |
| Owner can remove any pending order and handle refunds manually off-chain; users cannot cancel queued orders on-chain | Explicit trust model | Do not promote as permissionless victim impact |
| LayerZero delegate controls peers/DVNs/confirmations; destination trusts configured peer | Explicit trust model | No privileged-config test |
| Quote signer chooses route, amounts, receiver, deadline and fees; quotes are bearer instruments | Explicit trust model | Quote signer misuse is not an unprivileged bug |

## 4. Audit findings reconciled with current source history

Audit PDFs are historical evidence, not proof a defect remains in current deployed code. Reports often cover earlier `paxoslabs/nucleus-boring-vault` commits, whereas today's scoped contracts are deployed addresses in `pxl-boring-vault`. Do not call them unaudited, and do not submit issues acknowledged/resolved in a report.

### 4.1 TransitStation reports

**yAudit**, June 16–18, 2026:
- Repository in report: `paxoslabs/nucleus-boring-vault`
- Reviewed commit: `5affe77657a9bf788a6f13c27f911047d8900616`
- Final commit: `4a0d21ec5837842cfdb8936816c5e248e5e68c10`
- Findings/statuses:
  - Same-chain order submission could retain accidental native value — fixed in `cff03ae`.
  - Removing a peer does not immediately disable established inbound routes — acknowledged.
  - Cross-chain dust orders may collect source funds but truncate destination `amountDue` to zero — acknowledged.
  - `_pushOrder` lacked local UUID idempotency guard — fixed in `fc99730`.
  - No code-existence check on `_authority` — acknowledged as intentional because zero authority supports owner-only operation.
  - Recovery functions lacked events — fixed in `b1d6ac7`.
  - Additional informational findings in the report include peer removal, dust orders, constructor validation and recovery observability.
- Relevance: dust/zero-due, route-disable, peer-backlog and idempotency lines are prior-art. Do not make them fresh candidates absent a distinctly different, in-scope failure outside the reported behavior.

**Guardian**, June 22–24, 2026:
- Repository in report: `nucleus-boring-vault`
- Main review commit: `2a32b7cc3dfe83825cf9cc5a8cbe751dec95b122`
- Findings/dispositions: sub-dust orders with zero `amountDue` (M-01, acknowledged); refunded in-flight order can execute (M-02, resolved); version-skewed payload corrupts order (L-01, acknowledged); stale `executePendingOrders` decoder (L-02, resolved); depeg controls do not gate queued fills (L-03, acknowledged); quote signer can redirect receiver (L-04, acknowledged); `quoteSend` fee when gas limit unset (I-01, acknowledged); stale receive-route docs (I-02, resolved); disabled peer backlog (I-03, acknowledged); same-chain `msg.value` NatSpec/code mismatch (I-04, resolved); one bad fill may revert a batch (I-05, acknowledged).

**Pashov**, June 25–27, 2026:
- Reviewed `paxoslabs/nucleus-boring-vault` commit `f0007998e7e13ce34363f14b587a1a4d1d9f7aa8`; fixes review commit `094289219a4ace472e7b6be06187266c4aecaed3`.
- `L-01` stale `executePendingOrders` signature prevented Merkle-verified execution — resolved.
- `L-02` very low-decimal stablecoins could round the protocol fee to zero — acknowledged.
- Do not repackage either as an original candidate without a distinctly different, demonstrated impact and a new scope/eligibility basis.

### 4.2 PAXGy Equivalent Exchange / fee-module audits and follow-up

**Pashov**, reviewed at `0af42540fb25a1e5ea85b7142adb4f3a3b7954d5`:
- `L-01` stale gold prices while market closed — acknowledged.
- `L-02` fixed withdrawal fee inflated by PAXG premium — fixed in `23cd220`.
- `L-03` mismatched timestamps in PAXG/XAU feed create distorted rate — acknowledged.
- `L-04` Distributor deposits record share locks/refunds against wrong address — acknowledged.
- `L-05` strategist could leave lasting token approval — fixed in `ce9c62e`.

**yAudit**, August 5–15, 2026, PR #324:
- Reviewed commit `0af42540fb25a1e5ea85b7142adb4f3a3b7954d5`; final report commit `ae5c652339ba0c144fad61b752f8581188dd1215`.
- Findings include a High finding for a nested flash-loan batch escaping approval inspection; low findings around forced processing and tokens with `increaseApproval`; a deployment-salt issue; and informational findings around snapshot comments, received-vs-sent subsidy accounting, mixed-basket rescaling, PAXG/XAU feed timestamp skew, redundant UManager config, design-doc mismatch and Permit2 approvals.
- Follow-up [PR #342](https://github.com/paxoslabs/pxl-boring-vault/pull/342), “Audit fixes for EE UManager and PAXGy fee modules”, merged **2026-09-08** at `68c0a8b589bef3d284942af5da1fad0f39cdbea0`. It adds rejection of Balancer flash-loan calls in the inspected EE batch, checks `approve`, `increaseAllowance` and `increaseApproval` for dangling allowances, rejects lossy mixed-basket scale configs, adjusts fee math and fixes deployment-salt handling. These are documented historical issues; current source must be rechecked before concluding resolution, and nothing here is a fresh finding.

### 4.3 Scope relevance limit

The scoped deposit fee contract at `0x6E0A...8c6D` is `DCDAssetSpecificFeeModule`, not `PaxgyDynamicDepositFeeModule`. The Pashov/yAudit dynamic fee and Equivalent Exchange UManager findings therefore do not automatically refer to that scoped address. They remain useful cross-component history, but a candidate must map to a currently listed address and its exact implementation before the audit is considered directly applicable.

## 5. Candidate status and safe next action

| Candidate line | Status after audit/known-issue review | Decision |
|---|---|---|
| Cross-chain dust / zero destination `amountDue` | `KILLED / KNOWN ISSUE` (yAudit, Guardian, and Pashov findings) | Do not test or report as new |
| Low-decimal zero protocol fee | `KILLED / ACKNOWLEDGED AUDIT ISSUE` | Do not test or report as new; small rounding issue also faces $100,000 loss threshold |
| Disabled-peer route collection/backlog | `KILLED / ACKNOWLEDGED AUDIT ISSUE` | Do not repeat |
| No local UUID idempotency on `_pushOrder` | `KILLED / REPORTED; FIX MARKED` | Current source shows used-digest guards; no repeat |
| Stale decoder / selector mismatch | `KILLED / RESOLVED AUDIT ISSUE` | Do not repeat |
| Refunded in-flight order execution | `KILLED / RESOLVED AUDIT ISSUE` | Do not repeat |
| DCD supply cap across chains | `KILLED / KNOWN ISSUE` | Do not repeat |
| WQ refund-recipient, unfiltered transferable receipt, raw-hash signature, processor gas refund | `KILLED / KNOWN ISSUE` | Do not repeat |
| EE flash-loan / dangling-approval gap | `REPORTED; follow-up fix merged` | Do not resurrect without evidence of a distinct residual issue against exact in-scope deployed source; current EE manager is not a separately listed scope row |
| Oracle timestamp skew / depeg price distortion in dynamic PAXGy fee modules | `ACKNOWLEDGED AUDIT ISSUE` | Do not test the pricing-oracle interaction; program explicitly restricts oracle/third-party contract testing |
| Other Transit quote/signature/domain/replay properties | `RECONNAISSANCE` only | May return to static-only review after exact source comparison and complete remaining audit coverage; no PoC yet |
| Other queue/accountant/authority behaviors | `BLOCKED: source mismatch or source mapping open` | Resolve similar-match diffs and deployed state before choosing any local experiment |

### Hard gates

- Full 14-row inventory: **CLOSED**.
- Current official known-issues body read: **CLOSED** for documented items in this file.
- TransitStation and DCD deployed compiler/source metadata: **ESTABLISHED**; complete source-byte comparison for TransitStation still open due the single NatSpec discrepancy.
- Accountant / WithdrawQueue / WithdrawQueue fee source equivalence: **OPEN** (Etherscan Similar Match).
- Remaining scoped-address mappings: **OPEN**.
- Program-specific initial-discovery deadline: **UNKNOWN**; confirm through official program channel.
- Oracle/third-party testing: **PROHIBITED absent clear written authorization**.
- A new deterministic PoC: **NOT STARTED**; no test worth running until a distinct non-known invariant survives scope, audit, source and impact gates.

No vulnerability is claimed by this document. No report has been prepared or submitted.
