# Opportunity Monitor — 2026-10-20

**Status:** REVIEW COMPLETE — SOURCE-VERIFIED CHANGES RECORDED  
**Repository:** `Loofy147/Bounties`  
**Repository state observed:** `main` at `4ccc8292f89bd78ea0f76ddb962e85aa13b10cdd`  
**Previous status snapshot:** `CURRENT_STATUS_2026-09-29.md`

## Executive decision

1. **Keep 1inch Smart Contracts / Limit Order Protocol as the first track, but do not resume the old H-E2 line mechanically and do not submit it now.** The official program scope page shows eight assets marked new on 2026-10-14, including `Limit Order Protocol - new`. It also states that only the latest eligible tag/releases qualify and that reports must be submitted within 24 hours of initial discovery.
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

### Scope delta — ESTABLISHED

The scope page now lists these eight entries as added on 2026-10-14:

- Limit Order Protocol - new
- Limit Order Settlement - new
- Token-plugins - new
- Farming Contracts - new
- Delegating Contracts - new
- Cross-chain Swap - new
- Solana Crosschain - new
- Solana Fusion - new

The previous Bounties snapshot predates this page update. This is a material scope-page change and requires a fresh target-to-source mapping before any new testing. The parsed page did not expose a source URL for the specific “Limit Order Protocol - new” row, so the exact source/asset mapping for that row remains **OPEN**; do not infer it solely from the row label.

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

The 2026-09-29 research status records H-E2 local behavior as `EXPERIMENTALLY_SUPPORTED`, but the overall candidate remains `HYPOTHESIS`; bounty eligibility was still open. The status also records an unresolved resolver-role/privileged-address question, incomplete audit/known-issue reconciliation, and incomplete production prevalence evidence.

The 24-hour initial-discovery reporting rule is an additional blocker. Existing H-E2 work predates the 2026-10-14 scope-page update. **Do not assume that adding or relabeling a scope asset resets the initial-discovery clock.** Treat eligibility of this old candidate as `UNKNOWN / NOT CLEARED` unless Immunefi/1inch explicitly confirms otherwise. Do not submit based only on local reproduction or the new scope row.

Stop repeating synthetic variants of the same H-E2 mechanism unless genuinely new evidence changes a previously open gate. The next useful work is:
1. Map the current “Limit Order Protocol - new” asset to its exact eligible source and release commit.
2. Reconcile the matching audit archive, known issues, and previous disclosures against that exact code.
3. Determine whether resolver/access-token-holder treatment changes the in-scope assessment.
4. Choose a fresh, falsifiable invariant-based investigation only after the preceding gates pass.
5. Record the first-discovery timestamp for any genuinely new candidate and use a 24-hour submission gate.

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
