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
- Information and scope pages observed as last updated: 2026-10-21.
- Maximum reward: $500,000; payout in USDG on Ethereum, reward values denominated in USD.
- Critical: 10% of directly affected funds, minimum $10,000 / maximum $500,000.
- High: $5,000–$10,000.
- Medium: $1,000 flat.
- KYC required; PoC required; Responsible Publication Category 3 (approval required).
- The scope page states 14 assets total. Its extracted first page shows 12 assets; the two rows on page 2 are not included here because they have not been independently captured. Do not infer their names or addresses.
- The program scopes contracts by deployed address. If a listed asset is a proxy, the implementation it points to at submission time is included.
- A PoC must reproduce the impact against the in-scope contracts in a local or forked environment. Theoretical-only reports are out of scope.

**UNKNOWN**
- Initial-discovery/report deadline specific to this program. The checked information/scope pages did not establish a number of hours. Treat the gate as open and confirm via the official channel; do not interpret missing text as “no deadline”.
- Any change in rewards or terms relative to the previous day's snapshot, beyond the now-visible page-update date; current terms are the ones above.
- Exact deployed-source correspondence for each address in the table below.

## 2. Exact addresses visible on page 1

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
| PAXGy DCD FeeModule | `0x6E0A209672f6e357B2B5435AB6AEa2acbB4B8c6D` | [Etherscan](https://etherscan.io/address/0x6E0A209672f6e357B2B5435AB6AEa2acbB4B8c6D) |

**Asset inventory gate: OPEN.** Do not test or select a target as “the full scope” until page 2 has been captured and the remaining two assets recorded.

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
| PAXGy dynamic deposit fee | [`src/helper/PaxgyDynamicDepositFeeModule.sol`](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/helper/PaxgyDynamicDepositFeeModule.sol) | `2d5ee5f7b8c01ac29c6360f19a8a01af26f6e84e` |
| PAXGy dynamic withdrawal fee | [`src/helper/PaxgyDynamicWithdrawalFeeModule.sol`](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/helper/PaxgyDynamicWithdrawalFeeModule.sol) | `6b0f95e811fe502f83cb3e1d61265ea9f6e6f630` |
| Accountant | [`src/base/Roles/AccountantWithRateProviders.sol`](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/base/Roles/AccountantWithRateProviders.sol) | `35c34e1d2c01b648a1dc07ca9576101a1dc5987f` |
| Merkle Manager | [`src/base/Roles/ManagerWithMerkleVerification.sol`](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/base/Roles/ManagerWithMerkleVerification.sol) | `28eefd3c1ffdda1ee961c6d32279ff85a8d67d6f` |
| Teller | [`src/base/Roles/TellerWithMultiAssetSupport.sol`](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/base/Roles/TellerWithMultiAssetSupport.sol) | `a3293adf6ba70bef8a55b09a45130841d2e76c1b` |
| WithdrawQueue | [`src/base/Roles/WithdrawQueue.sol`](https://github.com/paxoslabs/pxl-boring-vault/blob/2843ac873718e869ac138278f9f4ee3c12736544/src/base/Roles/WithdrawQueue.sol) | `f0b60a43f77567481d2d907e75b7bfee90e81a8d` |

`deployment-config/PAXGyCCIPEth.json` at this commit matches four visible scoped addresses: PAXGy Token BoringVault, Manager, Accountant and RolesAuthority. The checked config's Teller address is zero, so it does not establish the deployed Teller source/pin.

This mapping is **not** sufficient to establish exact deployed-source equivalence. The following have not been established for any selected target:
- address and chain at the exact pinned block;
- runtime bytecode hash;
- verified source and exact compiler/settings;
- constructor arguments and immutable values;
- proxy status and implementation address, if applicable;
- repository commit/build metadata that recreates the deployed bytecode.

Do not infer eligible tag/release from `master` or a package version. Scope is the deployed address; deployment bytecode correspondence is the required pin.

## 4. Relevant official audit map — coverage is not yet reconciled

The official program information page links these reports in the program-owned source tree:

| Component family | Report | Official completion date |
|---|---|---|
| Core BoringVault | 0xMacro / Spearbit / Pashov | 2024 |
| WithdrawQueue | Zellic Zenith / Pashov | 2025–2026 |
| Predicate freeze / supply cap | Pashov | 2026-03-05 |
| TransitStation | yAudit | 2026-06-18 |
| TransitStation | Guardian | 2026-06-24 |
| TransitStation | Zellic | 2026-06-26 |
| TransitStation | Pashov | 2026-06-27 |
| PAXGy fee modules | Pashov | 2026-08-06 |
| PAXGy fee modules | yAudit | 2026-08-15 |
| CCIP Teller | Pashov | 2026-08-28 |

The report inventory does not establish which exact functions, revisions, deployed addresses, or known findings each report covers. The PDFs have not been text/image reviewed in this snapshot. No finding may be called “unaudited” from this list alone.

Audit links are available under [the repository's `audit/` folder](https://github.com/paxoslabs/pxl-boring-vault/tree/2843ac873718e869ac138278f9f4ee3c12736544/audit) and on the [official Immunefi information page](https://immunefi.com/bug-bounty/paxos-labs/information/).

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

Official link: https://docs.google.com/document/d/14gImubrl0MNn_Jl_2_jCW1QPD4ra_MqYX-TV8S7JGlQ/edit

The document could not be read through the current retrieval route. A previous monitor note reported that it contains entries involving DCD supply-cap behavior, share-lock fields, WithdrawQueue refund/receipt behavior, raw-hash queue signatures, gas-limit refunds, CCIP rate limits, decoder and pause behavior, role powers, and Merkle-verification cases. Treat that list as a **provisional research index only**, not a verified current known-issue ledger; check the primary document itself before assigning novelty status. This gate remains **OPEN**.

## 7. Invariant-led research queue

These are investigation directions, not vulnerability claims.

### PX-TR-01 — Signed quote and settlement-state integrity

Source family: `TransitStation`.

Candidate invariants:
- A quote digest must bind the exact route, chain/domain, verifying contract and order terms.
- A digest may be accepted only once at the source, and a cross-chain order UUID may enter destination pending state only once from the authenticated peer.
- Net offer tokens transferred must equal the signed offer amount after exactly the signed fee partition.
- Destination `amountDue` must derive deterministically from the normalized net amount and actual configured want-asset decimals.
- Partial fills must monotonically decrease `amountDue`; cumulative fills must not exceed it; the receiver and want asset must remain fixed.
- Batch failure must roll back state changes and transfers atomically.

Source observations at the recorded commit:
- EIP-712-like quote domain binds live `block.chainid` and `address(this)`.
- `_verifyAndCollect` marks the digest used before token transfers and partitions protocol fee, integrator fee and net.
- `_lzReceive` rejects a UUID already marked used on destination.
- `executePendingOrders` decrements/deletes order state before token transfer and checks the residual allowance after each batch.
- `_toNormalizedDecimals` / `_toTokenDecimals` deliberately truncate precision in documented paths.

**Interpretation:** these observed structures look like explicit mitigations, not evidence of a defect. Start by mapping deployed source and reviewing audit coverage. Small rounding/dust cases are not a priority because of the USD 100,000 threshold.

### PX-PX-01 — Fee module and share/NAV conservation

Source family: `PaxgyDynamicDepositFeeModule`, `PaxgyDynamicWithdrawalFeeModule`, `DistributorCodeDepositor`, `TellerWithMultiAssetSupport`, `AccountantWithRateProviders`, and any scoped queue/module revealed by page 2.

Candidate invariants:
- Deposit fee is within the original deposit amount and the net deposited amount equals the signed/authorized amount minus the fee.
- Minimum-mint failure and supply-cap failure revert the whole transaction, including prior transfers/mints.
- Deposit/withdrawal fees route only according to the deployed fee recipient/module configuration.
- Vault-held shares, total supply and NAV are treated consistently; do not assume the intended economic result from a comment alone.
- Exchange rate/fees state stays within documented bounds and pause behavior is enforced.

Source observations at the recorded commit:
- Deposit module rejects unexpected token/share addresses and rounds its fee up in the vault's favor.
- `DistributorCodeDepositor._deposit` deducts the fee, uses the Teller to mint, sends shares, then enforces the value-based supply cap; EVM revert should roll back the full call sequence.
- The withdrawal module's comment says shares sent to the vault are not burned, and that accounting must exclude vault-held shares from NAV/supply assumptions for the fee to accrue as intended.

**Interpretation:** the share/NAV note is a cross-component configuration/accounting question, not a proven defect. Check deployed fee module, queue/fee recipient and actual NAV/share-supply treatment against the known-issues ledger and relevant fee-module audit before designing an experiment.

### PX-AUTH-01 — Merkle manager and decoder boundary

Candidate invariants:
- Permission checks bind the deployed Merkle root, target, value, selector and sensitive decoded arguments.
- A different encoding or decoder interpretation must not authorize a call outside the committed permission.
- Only currently configured roles can perform the protected action.

**Gate:** do not hypothesize impact from missing/possible role configuration alone; the deployed settings must contain the relevant condition or the in-scope logic must allow an unprivileged actor to create it.

## 8. Implementation steps and gate statuses

| Gate | Status | Closure evidence |
|---|---|---|
| Official program/reward/PoC/KYC rules | `ESTABLISHED` | Live official pages |
| 14/14 scope row inventory | `OPEN` | Capture scope page 2 and the exact two remaining rows |
| Source commit identified | `ESTABLISHED` for repository snapshot only | Commit `2843ac8...` |
| Deployment bytecode → source equivalence | `OPEN` | Per-address chain/block, code hash, verified-source/compiler and build match |
| Full known-issues ledger read | `OPEN` | Read official linked document directly and cite exact applicable entries |
| Relevant audit contents reconciled | `OPEN` | Inspect reports and map findings to the selected code revisions |
| Testing restriction clarified for third-party/oracle behavior | `OPEN` | Written official clarification or avoid such interactions |
| Program-specific first-discovery deadline | `UNKNOWN` | Confirm through authorized program channel |
| Candidate invariant selected | `OPEN` | Close preceding scope/source/audit gates first |
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
