# Paxos Labs — Bounty Research Dossier

**Snapshot date:** 2026-10-21  
**Classification:** `RECONNAISSANCE` only  
**No vulnerability established. No candidate reproduced. No report prepared or submitted.**

## 1. Official program boundary

- Information: https://immunefi.com/bug-bounty/paxos-labs/information/
- Scope: https://immunefi.com/bug-bounty/paxos-labs/scope/
- Resources: https://immunefi.com/bug-bounty/paxos-labs/resources/
- Program-owned source: https://github.com/paxoslabs/pxl-boring-vault
- Known issues: https://docs.google.com/document/d/14gImubrl0MNn_Jl_2_jCW1QPD4ra_MqYX-TV8S7JGlQ/edit

**ESTABLISHED at check time**
- Live since: 2026-10-20.
- Information and scope pages observed in official search-indexed results as last updated: 2026-10-20 (checked 2026-10-21).
- Maximum reward: $500,000; payout in USDG on Ethereum, reward values denominated in USD.
- Critical: 10% of directly affected funds, minimum $10,000 / maximum $500,000.
- High: $5,000–$10,000.
- Medium: $1,000 flat.
- KYC required; PoC required; Responsible Publication Category 3 (approval required).
- The official scope UI was paginated. Both pages have now been reviewed and all **14/14** displayed rows are recorded below; page 2 contains WithdrawQueue and its fee module.
- The program scopes contracts by deployed address. If a listed asset is a proxy, the implementation it points to at submission time is included.
- A PoC must reproduce the impact against the in-scope contracts in a local or forked environment. Theoretical-only reports are out of scope.

**UNKNOWN**
- Initial-discovery/report deadline specific to this program. The checked information/scope pages did not establish a number of hours. Treat the gate as open and confirm via the official channel; do not interpret missing text as “no deadline”.
- Any change in rewards or terms relative to the previous day's snapshot, beyond the now-visible page-update date; current terms are the ones above.
- Exact deployed-source correspondence for each address in the table below.

## 2. Exact addresses — all 14 rows captured

Every entry below was read from the live official Immunefi scope table on 2026-10-21. The page shows each was added on **2026-10-05**.

| Program label | Address | Source/link |
|---|---|---|
| TransitStation | `0x49AAA987b1a7e9E4AE091dcD8332c39F322D7d28` | [Etherscan](https://etherscan.io/address/0x49AAA987b1a7e9E4AE091dcD8332c39F322D7d28) |
| Transit BoringVault | `0x91FE06C6E9F97E7DE4580A280E03046155f8e1e3` | [Etherscan](https://etherscan.io/address/0x91FE06C6E9F97E7DE4580A280E03046155f8e1e3) |
| Transit Manager | `0x666156ab52bb9984F5c3985726f048Dd4A73887a` | [Etherscan](https://etherscan.io/address/0x666156ab52bb9984F5c3985726f048Dd4A73887a) |
| Transit RolesAuthority | `0x3B4decc43d2173280198B46532Ef570062FCc8f5` | [Etherscan](https://etherscan.io/address/0x3B4decc43d2173280198B46532Ef570062FCc8f5) |
| Transit Decoder | `0xF34942E8612ccE476307B30a6246B43ce42B5D20` | [Etherscan](https://etherscan.io/address/0xF34942E8612ccE476307B30a6246B43ce42B5D20) |
| PAXGy Token BoringVault | `0x6c6494Fd9962eB98B94ffA48F6679058F820700e` | [Etherscan](https://etherscan.io/address/0x6c6494Fd9962eB98B94ffA48F6679058F820700e) |
| PAXGy Manager | `0x353741aBa79974a90F88594f6CBd1a9c54651015` | [Etherscan](https://etherscan.io/address/0x353741aBa79974a90F88594f6CBd1a9c54651015) |
| PAXGy Accountant | `0x397e38359f169748a02bc11f98D4f451FE88C1fd` | [Etherscan](https://etherscan.io/address/0x397e38359f169748a02bc11f98D4f451FE88C1fd) |
| PAXGy Teller | `0x41AB5d8387e60E30AACCF11357C306f6d875A6f7` | [Etherscan](https://etherscan.io/address/0x41AB5d8387e60E30AACCF11357C306f6d875A6f7) |
| PAXGy Roles Authority | `0xC444dA4DF6AF6A9A3891a720c1712a4188d899DD` | [Etherscan](https://etherscan.io/address/0xC444dA4DF6AF6A9A3891a720c1712a4188d899DD) |
| PAXGy DistributorCodeDepositor | `0xF6dE922D08cF9Ee4e7cE25ca1f3936EC1AA1f62C` | [Etherscan](https://etherscan.io/address/0xF6dE922D08cF9Ee4e7cE25ca1f3936EC1AA1f62C) |
| PAXGy DCD FeeModule (`DCDAssetSpecificFeeModule`) | `0x6E0A209672f6e357B2B5435AB6AEa2acbB4B8c6D` | [Etherscan](https://etherscan.io/address/0x6E0A209672f6e357B2B5435AB6AEa2acbB4B8c6D#code) |
| PAXGy WithdrawQueue | `0x69e0BF658bE5600864A946b4e5B911736D248FB4` | [Etherscan](https://etherscan.io/address/0x69e0BF658bE5600864A946b4e5B911736D248FB4#code) |
| PAXGy WithdrawQueue Fee Module (`WithdrawQueueAssetSpecificFeeModule`) | `0xF41e79D6e646f334C2fc4ea5Ae609707AE82264D` | [Etherscan](https://etherscan.io/address/0xF41e79D6e646f334C2fc4ea5Ae609707AE82264D#code) |

**Asset inventory gate: CLOSED (14/14).** Per-address source-to-deployment and configuration gates remain independently open; completing the table does not authorize a test.

## 3. Source provenance and what it proves

Program-owned repository:
- Repository: https://github.com/paxoslabs/pxl-boring-vault
- Observed `master` commit: [`2843ac873718e869ac138278f9f4ee3c12736544`](https://github.com/paxoslabs/pxl-boring-vault/commit/2843ac873718e869ac138278f9f4ee3c12736544)
- Committer date: 2026-10-14T22:14:06Z
- Commit message: merge of PR #363, “Createx parameters fix for withdrawqueue and repo as a whole”.

The current tree contains relevant source and tests:

| Component | Path at the observed commit | Blob SHA |
|---|---|---|
| TransitStation | [`src/transit/TransitStation.sol`](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/transit/TransitStation.sol) | `d83ef26ca09749a8503c9447d586449d45d46261` |
| DistributorCodeDepositor | [`src/helper/DistributorCodeDepositor.sol`](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/helper/DistributorCodeDepositor.sol) | `68521bf60f46bb4052543780d58c7b3b9270fdf0` |
| DCD deposit fee module (matches the scoped fee address) | [`src/helper/DCDAssetSpecificFeeModule.sol`](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/helper/DCDAssetSpecificFeeModule.sol) | `f79f17a6a45724598f061488b8eccb053a41c398` |
| WithdrawQueue fee module | [`src/helper/WithdrawQueueAssetSpecificFeeModule.sol`](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/helper/WithdrawQueueAssetSpecificFeeModule.sol) | `0d4530eb300908f99abb08c09a2142193b72e20e` |
| Accountant | [`src/base/Roles/AccountantWithRateProviders.sol`](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/base/Roles/AccountantWithRateProviders.sol) | `35c34e1d2c01b648a1dc07ca9576101a1dc5987f` |
| Merkle Manager | [`src/base/Roles/ManagerWithMerkleVerification.sol`](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/base/Roles/ManagerWithMerkleVerification.sol) | `28eefd3c1ffdda1ee961c6d32279ff85a8d67d6f` |
| Teller | [`src/base/Roles/TellerWithMultiAssetSupport.sol`](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/base/Roles/TellerWithMultiAssetSupport.sol) | `a3293adf6ba70bef8a55b09a45130841d2e76c1b` |
| WithdrawQueue | [`src/base/Roles/WithdrawQueue.sol`](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/base/Roles/WithdrawQueue.sol) | `f0b60a43f77567481d2d907e75b7bfee90e81a8d` |

`deployment-config/PAXGyCCIPEth.json` at this commit matches four visible scoped addresses: PAXGy Token BoringVault, Manager, Accountant and RolesAuthority. The checked config's Teller address is zero, so it does not establish the deployed Teller source/pin.

The mapping is now address-aware but not fully closed. Verified-source evidence checked on 2026-10-21:

| Scoped component | Explorer verification | Current repo comparison | Decision |
|---|---|---|---|
| TransitStation | Etherscan Exact Match; Sourcify `exact_match`; Solidity 0.8.21, optimizer 200, Shanghai | Sourcify source text is normalized-equal after replacing only the `forceSetUsedDigestTrue` NatSpec phrase (“becoming received” vs “being received”); raw text differs by three characters. Direct diff vs Pashov follow-up commit `094289219a4ace472e7b6be06187266c4aecaed3` found only `OrderSubmitted` event declaration/emission shape plus that comment phrase. State-transition logic aligns with the audit/fix source family; this does not prove bytecode identity | Normalized source text aligns with the pinned repo; no other source-file line differences were found against the Pashov follow-up source beyond the event ABI/log payload and comment. Runtime build, dependencies, and constructor/immutable mapping remain open |
| DCDAssetSpecificFeeModule | Etherscan Exact Match; Solidity 0.8.21, optimizer 200, Shanghai | Sourcify source text equals the pinned repo file exactly | Source text gate closed; deployed fee data/owner/constructor state remain open |
| PAXGy Accountant | Etherscan Similar Match; Solidity 0.8.21, optimizer 200, Shanghai | Not proven equivalent to pinned `AccountantWithRateProviders.sol` | Block this target until diff reconciled |
| WithdrawQueue | Etherscan Similar Match; Solidity 0.8.21, optimizer 200, Shanghai | Not proven equivalent to pinned `WithdrawQueue.sol` | Block this target until diff reconciled |
| WithdrawQueue fee module | Etherscan Similar Match; Solidity 0.8.21, optimizer 200, Shanghai | Not proven equivalent to pinned `WithdrawQueueAssetSpecificFeeModule.sol` | Block this target until diff reconciled |
| Other ten/authority/decoder targets | Some Sourcify records exist; exact repository commit mapping is inconsistent or unverified | Do not assume a default-branch file is deployed | Per-address pin required before selection |

Detailed row-level state and audit findings: [`AUDIT-AND-KNOWN-ISSUES_2026-10-21.md`](AUDIT-AND-KNOWN-ISSUES_2026-10-21.md).

This mapping is **not** sufficient to establish exact deployed-source equivalence for every asset. The following remain open:
- address and chain at the exact pinned block;
- runtime bytecode hash;
- verified source and exact compiler/settings;
- constructor arguments and immutable values;
- proxy status and implementation address, if applicable;
- repository commit/build metadata that recreates the deployed bytecode.

Do not infer eligible tag/release from `master` or a package version. Scope is the deployed address; deployment bytecode correspondence is the required pin.

## 4. Relevant official audit map

TransitStation audit PDFs and the PR #324 / #342 PAXGy fee-module audits have now been text-extracted and reconciled at the finding-title/status level. Reports on earlier `nucleus-boring-vault` commits are not proof that every currently scoped deployment is identical to the reviewed source, but their findings must be treated as prior art. See the [dated audit register](AUDIT-AND-KNOWN-ISSUES_2026-10-21.md).

- yAudit Transit: old repo commits `5affe77657a9bf788a6f13c27f911047d8900616` / `4a0d21ec5837842cfdb8936816c5e248e5e68c10`; dust-order and peer-removal issues acknowledged; `_pushOrder` idempotency and same-chain native-value handling marked fixed.
- Guardian Transit: old repo commit `2a32b7cc3dfe83825cf9cc5a8cbe751dec95b122`; sub-dust orders, version-skewed payload, peer backlogs and other listed findings include acknowledged/resolved entries.
- Pashov Transit: `L-01` stale decoder resolved; `L-02` zero fees for low-decimal stablecoins acknowledged.
- Pashov/yAudit PAXGy fee modules: review commit `0af42540fb25a1e5ea85b7142adb4f3a3b7954d5`; follow-up [PR #342](https://github.com/paxoslabs/pxl-boring-vault/pull/342) merged 2026-09-08. It includes a flash-loan nested-batch rejection, broader dangling-allowance checks, and fee/scaling/deployment corrections.

These reports have been text-extracted, not fully visually inspected. A final page-by-page visual review and exact deployed-implementation mapping remain open. Do not label a candidate “unaudited” or “novel” on this basis alone.

## 5. Testing and impact boundaries

**ESTABLISHED from the live official pages**
- In-scope contracts are those deployed at the listed addresses; proxies' live implementation is included.
- A local/forked PoC must reproduce all scenario conditions and the impact.
- Admin/privileged configuration is out of scope when the impactful configuration is possible but absent from the deployed system, unless the stated program exceptions apply.
- External service/infrastructure failure alone is out of scope; in-scope contract defects in integration handling may qualify.
- Non-standard token behavior is out of scope when the token is not enabled in the deployed system.
- Rounding/precision loss is out of scope unless the PoC demonstrates at least **USD 100,000** loss to the protocol or users.
- Undeployed scripts, mocks, tests, and other out-of-scope code are not bounty targets.
- Mainnet/public-testnet testing is prohibited.
- The information page prohibits testing with pricing oracles and third-party smart contracts. The scope page has narrower oracle-impact text. Treat the test restriction as the stricter rule: no such interaction without explicit written clarification.
- Public disclosure of an unpatched/embargoed finding, phishing/social engineering, third-party-system testing and DoS against project assets are prohibited.

**Impact target:** prioritize direct theft of user funds, permanent freezing, insolvency, or a specifically enumerated freezing/theft impact. Do not stretch these definitions to cover mere rounding, dust, admin preference, or unquantified accounting concern.

## 6. Known-issues gate

**CLOSED for the current document body** after direct extraction on 2026-10-21. The earlier note saying the document could not be read is superseded. The official document explicitly lists cross-chain DCD supply-cap limitations, non-enforcing share locks, WithdrawQueue refund-recipient and receipt-screening semantics, raw-hash queue signatures, processor-gas refund behavior, CCIP shared-rate-limit exhaustion, an infeasible Merkle double-preimage scenario, Transit decoder design, pause behavior, and trusted roles. Full details and explicit kill decisions are recorded in [`AUDIT-AND-KNOWN-ISSUES_2026-10-21.md`](AUDIT-AND-KNOWN-ISSUES_2026-10-21.md). These entries are exclusions, not hypotheses.

## 7. Candidate register after source/audit/known-issue triage

These are research lines, not vulnerability claims. Findings labelled known/audited are not to be repeated as new experiments.

| ID | Surface | Status | Rationale / decision |
|---|---|---|---|
| PX-TR-01 | Transit quote digest, chain/domain binding, replay and order settlement | `RECONNAISSANCE / BLOCKED` | The verified source is strongly mapped, but full normalized text equality and audit-to-deployed-source equivalence remain open. yAudit/Guardian/Pashov already cover several adjacent payload, idempotency, routing and execution behaviors. No target-interacting test until the residual property is distinct from documented findings. |
| PX-TR-02 | Cross-chain decimal normalization / dust / zero `amountDue` | `KILLED / KNOWN AUDIT ISSUE` | yAudit and Guardian reported sub-dust/zero-due behavior; Pashov acknowledged low-decimal fees rounding to zero. Do not repeat. Rounding/precision-only impact also faces the program's USD 100,000 loss threshold. |
| PX-TR-03 | Version-skewed payload and receive-side route behavior | `KILLED / ACKNOWLEDGED AUDIT ISSUE` | Guardian acknowledged a version-skewed payload; yAudit/Guardian acknowledge peer-removal/route backlog behavior. Do not repackage those reports. |
| PX-PX-01 | DCD fee arithmetic / deployed per-token config | `RECONNAISSANCE / CONFIGURATION GATE OPEN` | The scoped module is `DCDAssetSpecificFeeModule` (not the dynamic oracle fee module). Its fee settings are owner-controlled; the consuming deposit path reverts when fees equal/exceed deposit amount. Need deployed owner, fee mapping and DCD config before any candidate could exist. No serious unprivileged impact is currently supported. |
| PX-PX-02 | Cross-chain DCD supply cap | `KILLED / KNOWN ISSUE` | Official known-issues document explicitly says the cap is only single-chain enforceable. No repeat experiment. |
| PX-PX-03 | Dynamic PAXGy fee/oracle and share/NAV accounting | `BLOCKED / SCOPE MAPPING OPEN` | Dynamic fee modules appear in source/audit history but the scoped DCD fee address is a different contract. Pashov/yAudit recorded acknowledged feed freshness/skew/share-lock concerns and fixed fee math. The program restricts oracle/third-party interactions. Do not begin an experiment without matching a currently scoped address and resolving audit/known-issue overlap. |
| PX-WQ-01 | WithdrawQueue refund receiver, receipt transfer/screening, cancellation signatures | `KILLED / KNOWN ISSUE` | All listed behavior is in the official known-issues document. WithdrawQueue deployed source is an Etherscan Similar Match; do not explore a source variant before reconciling it. |
| PX-WQ-02 | WithdrawQueue processor gas, refund behavior, liveness | `KILLED / KNOWN ISSUE` | Processor gas-limited refund and queue liveness assumptions are explicitly documented and role-trusted. |
| PX-AUTH-01 | Merkle manager double-preimage / decoder sanitization | `KILLED / KNOWN ISSUE / DESIGN-BOUNDED` | The official known-issues document says the double-preimage scenario is not viable, and Transit decoder behavior is intentional and bounded by pending order, fixed receiver, amountDue and vault approval checks. Do not test. |
| PX-EE-01 | Equivalent Exchange nested flash-loan / dangling approval | `REPORTED / FOLLOW-UP FIX MERGED` | yAudit reported a High issue; PR #342 merged 2026-09-08 and adds a flashLoan rejection + checks additional approval selectors. EquivalentExchange UManager is not a separately listed target address, so do not treat its historical report as a new scoped candidate. |

### Candidate-selection decision

**No new invariant currently clears all serious-work gates.** The next safe engineering step is remaining deployment/source reconciliation, not a synthetic PoC:
1. Close the complete deployed build pin for TransitStation: compile the verified source set with exact dependencies/settings and reconcile constructor/immutable/runtime metadata. The current source's only difference from the Pashov follow-up source is event ABI/log payload and a NatSpec phrase; do not re-test known/fixed state-transition issues.
2. Compare the deployed Accountant, WithdrawQueue and WithdrawQueue fee-module sources against the pinned repo files. Etherscan reports Similar Match for those three.
3. Capture current deployed configuration for the DCD owner and per-token fee map, if that surface remains the chosen target; without it, do not infer impact from hypothetical privileged settings.
4. Recheck official known issues and current reward terms at the point a genuinely distinct property is proposed.
5. Only then design a local/fork harness against an invariant that is neither a known issue nor an acknowledged/resolved audit finding.

## 8. Implementation steps and gate statuses

| Gate | Status | Closure evidence |
|---|---|---|
| Official program/reward/PoC/KYC rules | `ESTABLISHED` | Live official pages |
| 14/14 scope row inventory | `ESTABLISHED` | All 14 live rows captured, including both page-2 queue entries |
| Source commit identified | `ESTABLISHED` for repo snapshot | Commit `2843ac873718e869ac138278f9f4ee3c12736544` |
| Deployment bytecode → source equivalence | `OPEN` | Per-address chain/block, code hash, verified-source/compiler and build match |
| Official known-issues document | `ESTABLISHED` for extracted document body | Read directly 2026-10-21; known exclusions mapped in the audit register |
| Audit finding-title/status pass | `ESTABLISHED` | Transit and relevant PAXGy fee PDFs text-extracted; exact current-source/final visual reconciliation remains OPEN |
| Testing restriction clarified for third-party/oracle behavior | `OPEN` | Written official clarification or avoid such interactions |
| Program-specific first-discovery deadline | `UNKNOWN` | Confirm through authorized program channel |
| Candidate invariant selected | `OPEN` | Remove known issues and close source-map gate before defining a distinct property |
| Deterministic local PoC | `NOT STARTED` | Only after target and test-policy gates permit the exact harness |
| In-scope impact, novelty and human review | `NOT STARTED` | Independent evidence package and current policy mapping |

## 9. Stop conditions

Stop or retain `RECONNAISSANCE` if:
- target is not one of the exact listed deployed addresses (or the included live implementation of a listed proxy);
- source-to-deployment correspondence is ambiguous;
- the only effect is theoretical, intentional, a best-practice recommendation, or a low-value rounding issue;
- the behavior is already covered as a known issue/audit finding;
- the scenario depends on unavailable/privileged state without a qualifying logic flaw;
- a PoC would violate local-only, third-party or oracle restrictions;
- impact does not meet a current in-scope impact definition.

Any report must be authored, reviewed, and submitted by the human researcher. Never submit an AI-generated report.
