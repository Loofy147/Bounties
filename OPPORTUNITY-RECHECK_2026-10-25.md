# Opportunity Recheck — 2026-10-25

**Classification:** Source-verified opportunity ranking; no vulnerability claim and no active testing performed.  
**Repository reviewed:** `Loofy147/Bounties`, `main` at `bbf4a323543462b6a71626d2b281246870d9b842`.  
**Ranking rule:** Advertised maximum bounty is only a ceiling, not expected value. The shortlisting also considers payout eligibility, actual published payout history, scope clarity, known-issue risk, and fit with our local-fork/invariant-testing workflow.

## Decision

The previous review's SP1 figure is stale. As of the official Immunefi page last updated **2026-10-23**, SP1 advertises **$15,000 maximum**, not $100,000. Keep SP1 as a low-payout specialist option, not the primary high-value target.

The existing 1inch H-E2/K-04 work remains **HYPOTHESIS / HOLD**. Its local behavior was experimentally reproduced, but eligibility is not cleared: its first-discovery reporting deadline, resolver-role interpretation, impact fit, deployment correspondence, and complete known-issue/audit reconciliation remain unresolved. Do not repeat synthetic variants of that same mechanism. The current 1inch program advertises $500,000 maximum, requires KYC, and says reports should be submitted within 24 hours of initial discovery.

Assuming the previously preferred **no-KYC payout constraint** still applies, the best high-cap candidates to investigate next are **Sky, GMX, and Spark**. No candidate is yet a finding.

## Ranked no-KYC shortlist

| Rank | Program | Advertised maximum | Official program signals | Principal cautions |
|---|---|---:|---|---|
| 1 | [Sky](https://immunefi.com/bug-bounty/sky/information/) | **$10,000,000** | KYC not required; Critical smart-contract reward $150,000 minimum; 255 assets in scope; published total paid $720,700 across 22 reports | Very broad asset surface; only deployed versions qualify; legacy vulnerabilities already mitigated are excluded; extensive audits and known-issue/deployment reconciliation required. Testing must use local forks; oracle and third-party-contract testing is prohibited. |
| 2 | [GMX](https://immunefi.com/bug-bounty/gmx/information/) | **$5,000,000** | KYC not required; Critical smart-contract reward has a $50,000 minimum; 250 assets in scope; published total paid $2.7M across 31 reports; median resolution time 10 hours | Numerous published known issues; scope includes GMX smart-contract repositories and listed assets; local-fork testing only, with pricing-oracle and third-party-contract testing prohibited. |
| 3 | [Spark](https://immunefi.com/bug-bounty/sparklend/information/) | **$5,000,000** | KYC not required; Critical smart-contract reward $50,000 minimum; 385 assets in scope; explicit Known Issue Assurance commitment | Broad scope; completed-audit issues are ineligible; only deployed-code vulnerabilities qualify; compensated contributors who wrote code for an in-scope asset are ineligible. Payouts are in DAI through governance; payouts over $1M are staged at up to $1M per following month after the first million. |
| 4 | [Origin Protocol](https://immunefi.com/bug-bounty/originprotocol/information/) | **$1,000,000** | KYC not required; Critical smart-contract reward has a $50,000 minimum; 64 assets in scope; published total paid $139,200 across 40 reports; median resolution time 7 hours | Smaller ceiling; confirm current asset/deployment map, audit exclusions and actual code path before selecting a hypothesis. |

### Why these ranks

- **Sky** is the highest advertised cap among the shortlisted no-KYC programs. Its size does not make it the easiest opportunity; deployed-version pinning and broad audit coverage are the main entry gates.
- **GMX** has the strongest publicly reported payout track record among these candidates and a comparatively short published median resolution time. That is not evidence a new finding will be accepted; the known-issue list must be used as a hard exclusion set.
- **Spark** is especially worth screening because its published Known Issue Assurance may reduce uncertainty about whether a valid, in-scope issue is already known. It does not remove the need for novelty checks or a runnable PoC.
- **Origin** is a lower-cap comparison candidate with fewer listed assets, useful if the first goal is a tractable, legitimate paid finding rather than the largest theoretical award.

## Highest caps overall — excluded from the no-KYC-first shortlist

| Program | Advertised maximum | Gate that changes prioritization |
|---|---:|---|
| [LayerZero](https://immunefi.com/bug-bounty/layerzero/information/) | **$15,000,000** | KYC required; critical reward is based on 10% of directly affected funds up to the cap; cross-chain/verification complexity is high. |
| [Stargate](https://immunefi.com/bug-bounty/stargate/information/) | **$10,000,000** | KYC required; Critical minimum $100,000; extensive bridge/audit surface. |
| [USDT0](https://immunefi.com/bug-bounty/usdt0/information/) | **$6,000,000** | KYC required; reports whose impacts are already covered by LayerZero can be forwarded there, so overlap/duplicate routing is a material concern. |
| [Ethena](https://immunefi.com/bug-bounty/ethena/information/) | **$3,000,000** | KYC required; specialist stablecoin mechanism and deployment/audit mapping required. |
| [1inch Smart Contracts](https://immunefi.com/bug-bounty/1inch-SmartContracts/information/) | **$500,000** | KYC required and 24-hour initial-discovery reporting rule; existing H-E2 eligibility remains uncleared. |

These caps are not directly comparable to likely payouts. Programs that calculate Critical rewards as a percentage of affected funds pay according to demonstrated impact and their rules, not simply the advertised maximum.

## Current repository candidates

- **1inch:** $500,000 maximum; KYC required; maintain H-E2/K-04 on hold. The $500,000 cap is real, but it does not fix the known eligibility problem.
- **SP1:** $15,000 maximum as of the 2026-10-23 update; KYC not required; runnable PoC required. The code is a RISC-V zkVM and requires specialist production soundness/completeness analysis, so reward-to-specialization trade-off is poor for the current high-value objective.
- **Cosmos:** $50,000 maximum; KYC required; official program page last updated 2026-10-20. Full scope, known issues, and payout eligibility were not re-audited in this pass.
- **IOTA / Sherlock:** remains `UNKNOWN`; no primary-source terms verified here.

## Execution gate before selecting a target

For **Sky, GMX, and Spark**, do not begin broad fuzzing yet. First create the same compact qualification packet for each:

1. Pin official scope page, current eligible deployment/release and immutable source commit.
2. Extract exact in-scope impacts, payout formula/minimum, KYC/eligibility, prohibited local-fork interactions, and all known-issue/audit exclusions.
3. Build a state/invariant map from the pinned code and select one falsifiable property per candidate.
4. Run only local, deterministic controls; retain passing controls and killed hypotheses as negative evidence.
5. Choose the target with the strongest new, testable invariant and smallest scope/novelty uncertainty—not the largest number on the listing.

**Stop conditions:** the candidate is already reported/known; vulnerable code is not deployed/in scope; impact wording does not match; test setup violates the rules; or no counterexample survives the controls. Never submit AI-generated reports; the final report must be human-authored/reviewed under the program's current rules.

## Official source pages checked on 2026-10-25

- [Immunefi current program directory](https://immunefi.com/bug-bounty/) — listing reports last updated 2026-10-24 16:00 UTC.
- [SP1 information](https://immunefi.com/bug-bounty/sp1/information/) — maximum $15,000; page last updated 2026-10-23; no KYC required.
- [Sky information and scope rules](https://immunefi.com/bug-bounty/sky/information/) — maximum $10,000,000; page last updated 2026-09-19; no KYC required.
- [GMX information and known issues](https://immunefi.com/bug-bounty/gmx/information/) — maximum $5,000,000; page last updated 2026-09-30; no KYC required.
- [Spark information](https://immunefi.com/bug-bounty/sparklend/information/) — maximum $5,000,000; page last updated 2026-09-18; no KYC required; Known Issue Assurance.
- [Origin Protocol information](https://immunefi.com/bug-bounty/originprotocol/information/) — maximum $1,000,000; page last updated 2026-09-07; no KYC required.
- [LayerZero information](https://immunefi.com/bug-bounty/layerzero/information/), [Stargate information](https://immunefi.com/bug-bounty/stargate/information/), [USDT0 information](https://immunefi.com/bug-bounty/usdt0/information/), and [Ethena information](https://immunefi.com/bug-bounty/ethena/information/) — high-cap comparison; KYC required for these four.
- [1inch Smart Contracts information](https://immunefi.com/bug-bounty/1inch-SmartContracts/information/) — maximum $500,000; page last updated 2026-10-14; KYC required.

**Status:** reconnaissance only. No vulnerability claimed, no external submission made, and no active testing performed by this review.
