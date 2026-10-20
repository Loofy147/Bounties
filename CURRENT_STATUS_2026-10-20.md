# Opportunity Monitor — 2026-10-20

**Status:** REVIEW COMPLETE — SOURCE-VERIFIED CHANGES RECORDED  
**Repository:** `Loofy147/Bounties`  
**Repository state observed:** `main` at `4ccc8292f89bd78ea0f76ddb962e85aa13b10cdd`  
**Previous status snapshot:** `CURRENT_STATUS_2026-09-29.md`

## Executive decision

1. **Keep 1inch in the active research queue, but correct the previous scope interpretation.** The information page was updated on 2026-10-14; the separate scope page shows last updated on 2026-08-14 and lists eight assets with `Added on` dates of 2026-06-10. I found no official evidence of a target named `Limit Order Protocol - new` or of an asset addition on October 14. The program requires the latest eligible tag/releases and reporting within 24 hours of initial discovery.
2. **SP1 is the best fallback to prepare, not an automatic switch.** It is a live zero-knowledge proof program with a $100,000 maximum, no payout KYC, and strict production soundness/completeness requirements.
3. **IOTA/Sherlock remains unpromoted.** This review did not independently verify the full official program terms from an accessible primary-source page; reward, eligibility, and KYC details must remain unconfirmed until rechecked directly.

No vulnerability is claimed or promoted by this review. No active testing was performed as part of this opportunity scan.

## 1. Primary opportunity: 1inch Smart Contracts

### Official program facts — ESTABLISHED

- Program page: https://immunefi.com/bug-bounty/1inch-SmartContracts/information/
- Scope page: https://immunefi.com/bug-bounty/1inch-SmartContracts/scope/
- Last updated shown by Immunefi: **2026-10-14**.
- Maximum advertised bounty: **$500,000**, paid in USDC on Ethereum.
- Reward bands shown: Critical $30,000–$500,000; High $10,000–$30,000; Medium $2,000–$10,000; Low $100–$2,000.
- PoC required for every severity.
- KYC required for payout processing.
- Scope applies only to the latest eligible tags/releases.
- Any vulnerability must be reported no later than 24 hours after initial discovery; late reports may be considered at the team's discretion but are not guaranteed reward eligibility.
- For a Critical reward, the demonstrated impact must also be live on a mainnet deployment. The program reserves discretion to downgrade impacts involving code not deployed on mainnet.
- Testing deployed mainnet/public-testnet code is prohibited; testing must use a local fork. Testing with third-party contracts is prohibited, except that integration logic may be tested on a local fork. Do not access or modify other users' data, conduct denial-of-service testing, or publicly disclose an unpatched/embargoed issue. AI-generated reports are explicitly prohibited.

### Scope delta — ESTABLISHED (corrected)

The current Immunefi pages show different page-update timestamps:
- Information page: last updated **2026-10-14**.
- Scope page: last updated **2026-08-14**.
- Each of the eight listed scope assets shows **2026-06-10** in its `Added on` column: Limit Order Protocol, Limit Order Settlement, Token-plugins, Farming Contracts, Delegating Contracts, Cross-chain Swap, Solana Crosschain, and Solana Fusion.

The scope table does not currently identify `Limit Order Protocol - new`, and does not show these eight assets as added on October 14. The verified change is an information-page update, not a demonstrated scope-asset addition. Do not report a new target without an official row and a verifiable scope delta.

### Version and provenance gate — OPEN

Existing Bounties record:
- Repository: https://github.com/1inch/limit-order-protocol
- Previously researched release tag: `4.3.4`
- Previously researched commit: `7da29889efa2e635611e1caf60f85f595ff7f05f`
- GitHub resolves commit ref `4.3.4` to that commit; the tagged `package.json` declares version `4.3.4`.

New repository observation:
- The current default-branch `package.json` declares `4.3.5`.
- The current default-branch commit observed in the GitHub API was `50bd1300315606a3d32e9021898374c9d0dc2335` (2026-09-24).
- A contents lookup at ref `4.3.5` returned “No commit found for the ref 4.3.5”. Therefore, the version string on default branch does **not** establish that an eligible `4.3.5` tag/release exists.
- Do not treat default-branch/WIP code as the bounty target. The repository README itself warns that default-branch code is work in progress and directs researchers to tagged commits.

Before any new test, determine from the current program asset link and release/tag metadata exactly which commit is eligible. If the program team does not expose an unambiguous mapping, request clarification through its authorized channel before testing.

### Existing H-E2 / K-04 line — HOLD

The 2026-09-29 research status records H-E2's local mechanism as `EXPERIMENTALLY_SUPPORTED`, while the overall candidate remains `HYPOTHESIS`. The new source review yields these separate results:

- **Scope correction — ESTABLISHED:** the information page was updated on 2026-10-14, but the current scope page says it was last updated on 2026-08-14 and lists eight assets with `Added on` dates of 2026-06-10. No current official evidence establishes a new asset named `Limit Order Protocol - new` or an October 14 asset addition.
- **Target pin — ESTABLISHED:** the official GitHub Releases page lists `v4.3.4` as the latest release at commit `7da29889efa2e635611e1caf60f85f595ff7f05f`. The default-branch package version `4.3.5` is not evidence of a published eligible tag.
- **Specific audit coverage — ESTABLISHED:** the official 1inch audit archive describes its `Limit Order Protocol v4.3.4` OpenZeppelin report as covering the `Permit2Proxy` extension. That report does not establish audit coverage of `NativeOrderFactory` or `NativeOrderImpl`. This does not prove the extension was never audited elsewhere.
- **Design-intent evidence — ESTABLISHED:** the public NativeOrder PR #390 explicitly discussed returning the full WETH balance, including accidentally deposited WETH, and the maintainer explained why that broad refund behavior was desired. This supports intended full-balance refund semantics; it does not establish that the undercollateralized resolver-reward scenario itself was known.
- **Reporting eligibility — NOT CLEARED:** local H-E2 work and impact calibration were already documented by 2026-09-29, while the live program page states a 24-hour initial-discovery reporting rule. A page update does not reset that clock. Late reports may be considered at program discretion, but reward eligibility is not guaranteed. Do not submit H-E2 unless the program explicitly confirms eligibility.

Do not repeat synthetic variants of the same H-E2 mechanism. The next useful action is to stop treating H-E2 as the immediate payout candidate, preserve its technical evidence, and run a distinct, falsifiable investigation against the pinned release only if its scope and expected impact justify the work. Any genuinely new issue must have its actual first-discovery timestamp recorded, and tests must remain local/fork-based under the current program terms.

Detailed source-by-source reconciliation: [`targets/1inch/AUDIT-AND-ELIGIBILITY-RECHECK_2026-10-20.md`](targets/1inch/AUDIT-AND-ELIGIBILITY-RECHECK_2026-10-20.md).

## 2. Fallback candidate: SP1

Official pages:
- Information: https://immunefi.com/bug-bounty/sp1/information/
- Scope: https://immunefi.com/bug-bounty/sp1/scope/
- Code: https://github.com/succinctlabs/sp1

Facts verified from the program pages:
- Live since 2026-09-21; page last updated 2026-10-19.
- Maximum bounty $100,000; USDC on Ethereum.
- No KYC information required for payout.
- Runnable PoC required for all severities.
- Scope assets were added on 2026-10-01, including `sp1-core-executor`, `sp1-core-machine`, `sp1-hypercube`, `sp1-recursion`, `sp1-zkvm`, `sp1-lib`, eligible SLOP components, and the SP1 prover verifier.
- Main eligible impacts are production soundness failures or protocol-level completeness failures. Critical requires false proofs across all four proof types for a general class of programs; the scope separately defines High and Medium proof impacts.
- Reports must match SP1's latest release commit and use production circuits and verification keys with production security checks. PoCs should execute on Apple M3 or equivalent hardware in ten minutes or less.
- Testing code deployed on mainnet/public testnet is prohibited; use local forks. Prover/verifier denial of service, service availability, debug/experimental paths, excluded SLOP components, and non-zero-exit-code verification findings are out of scope under the current page.

Relevance — **INFERENCE**: The Bounties/Moirae approach of state modelling, invariants, deterministic experiments, counterexample minimization, and evidence gates transfers well. The main gap is specialist zkVM/cryptographic-circuit knowledge; therefore begin with scope/audit/known-issue mapping and a local baseline, not unbounded fuzzing or a speculative vulnerability claim.

## 3. Candidate exclusion / uncertainty ledger

| Candidate | Current classification | Reason |
|---|---|---|
| 1inch LOP H-E2/K-04 | `HYPOTHESIS`; submission eligibility `UNKNOWN / NOT CLEARED` | Existing evidence is local; the program has a 24-hour initial-discovery rule; source/scope mapping and remaining gates are open. |
| SP1 | `RECONNAISSANCE` | Material recent scope addition and no KYC; high technical difficulty and tight PoC constraints. |
| IOTA / Sherlock | `UNKNOWN` | Primary-source terms and payout eligibility were not independently confirmed in this review. Do not use third-party summaries as the final eligibility basis. |
| Cosmos | Existing portfolio candidate; no new change validated here | Program page currently shows last updated 2026-10-13, $50,000 max, and KYC required, but this review did not establish a new scope/reward delta worth a new-opportunity alert. |

## 4. Monitoring and evidence rules

Every future alert must compare the current official page against the last recorded snapshot and include only a materially new program/asset or a meaningful change in scope, release eligibility, rewards, KYC, reporting deadline, permitted test environment, or known-issue policy.

For every proposed target, record:
- official information and scope URLs;
- page last-updated date and exact date the asset entered scope;
- asset/repository path and immutable commit/release;
- in-scope impact wording and explicitly excluded impacts;
- PoC requirement, allowed test environment, and prohibited actions;
- reporting deadline, disclosure rules, and payout eligibility/KYC;
- existing repository capability fit and material gaps;
- candidate status using the repository's evidence labels;
- next action and a stop condition.

Do not claim an exploit from a bounty listing. Do not recommend tests against assets or environments unless the current program explicitly authorizes them. Never submit an AI-generated report; use AI only as a research aid and produce the final submission through human review in accordance with program rules.

## Source links

- 1inch program information: https://immunefi.com/bug-bounty/1inch-SmartContracts/information/
- 1inch program scope: https://immunefi.com/bug-bounty/1inch-SmartContracts/scope/
- 1inch source repository: https://github.com/1inch/limit-order-protocol
- 1inch audit archive: https://github.com/1inch/1inch-audits
- SP1 program information: https://immunefi.com/bug-bounty/sp1/information/
- SP1 program scope: https://immunefi.com/bug-bounty/sp1/scope/
- SP1 repository and audits: https://github.com/succinctlabs/sp1/tree/main/audits
