# 1inch Audit and Eligibility Recheck — 2026-10-20

**Classification:** Evidence reconciliation; no vulnerability claim; no submission made.  
**Purpose:** Correct the October 20 opportunity-scan interpretation and close as many H-E2/K-04 eligibility gates as public evidence supports.

## 1. Official program facts

- Information page: https://immunefi.com/bug-bounty/1inch-SmartContracts/information/
- Scope page: https://immunefi.com/bug-bounty/1inch-SmartContracts/scope/
- Maximum listed reward: USD 500,000; payment in USDC on Ethereum.
- PoC required for every severity.
- KYC is required for payout processing.
- The current information page states any vulnerability must be reported within 24 hours after initial discovery. Late reports may be considered at 1inch's discretion, but reward eligibility is not guaranteed.
- The program page says only the latest eligible tags/releases qualify.
- Testing deployed mainnet/public-testnet code is prohibited; use local forks. Other prohibited activities include prohibited third-party contract testing, denial-of-service, public disclosure of embargoed unpatched issues, and submitting AI-generated reports.

## 2. Corrected page-date and scope reading

The pages have separate timestamps:
- Information page: last updated **2026-10-14**.
- Scope page: last updated **2026-08-14**.
- All eight visible assets show **2026-06-10** in the `Added on` column: Limit Order Protocol, Limit Order Settlement, Token-plugins, Farming Contracts, Delegating Contracts, Cross-chain Swap, Solana Crosschain, and Solana Fusion.

The current table does not show an asset named `Limit Order Protocol - new` or show these assets as added on October 14. The previous opportunity report conflated an information-page update with a scope change. That claim is corrected in `CURRENT_STATUS_2026-10-20.md`.

## 3. Exact target pin

Official release listing: https://github.com/1inch/limit-order-protocol/releases

The release page identifies `v4.3.4` as the latest public release and points to commit:

```text
tag:    4.3.4
commit: 7da29889efa2e635611e1caf60f85f595ff7f05f
```

The default-branch `package.json` declares `4.3.5`, but the public release page does not list a 4.3.5 release and GitHub did not resolve the `4.3.5` ref to a commit. Do not treat a default-branch package version as proof of an eligible release. The reproducible local target remains 4.3.4, subject to current program-to-repository asset mapping.

## 4. Audit and prior-disclosure reconciliation

### Specific published audit coverage — ESTABLISHED

Official audit archive:
https://github.com/1inch/1inch-audits

The archive README's `Limit Order Protocol v4.3.4` section describes the OpenZeppelin report as covering the **Permit2Proxy extension**, a simpler Permit2 integration without witness data. The archive path contains `Limit Order Protocol v4.3.4/1inch Limit Order Protocol v4.3.4_OpenZeppelin.pdf`.

That establishes the coverage described for this specific report. It does **not** establish that `NativeOrderFactory` or `NativeOrderImpl` were covered by this report; it also does not prove NativeOrder was never audited elsewhere.

### Public design-intent evidence — ESTABLISHED

NativeOrder implementation PR:
https://github.com/1inch/limit-order-protocol/pull/390

On September 24, 2025, review discussion explicitly asked whether the whole contract WETH balance should be returned, including accidentally sent WETH. The maintainer replied that this was intentional, citing WETH left after cross-chain order cancellation and the maker's ability to withdraw WETH. This is design-intent evidence for the **whole-balance refund path**.

It is not proof that the exact undercollateralized resolver-reward condition was known or disclosed. The condition is more specific: for residual maker balance (C < R), a resolver supplies enough WETH to make the clone balance reach the computed reward (R), and the resolver reward may then consume the maker's residual balance. That mechanism remains only experimentally supported by the old local record; it is not elevated to a confirmed vulnerability.

## 5. H-E2 / K-04 decision

Current technical label: `EXPERIMENTALLY_SUPPORTED` for the local behavior; overall security claim remains `HYPOTHESIS`.

Current eligibility gates:
- **Program impact mapping:** OPEN. The program lists direct theft/permanent freezing/insolvency as Critical impacts, but triage must decide whether this permissioned resolver path and demonstrated victim state meet its wording.
- **Resolver role:** OPEN. The resolver is a permissioned caller for resolver cancellation. The program's privileged-address exclusion names governance and strategist; do not assume the resolver's treatment without an evidence-backed interpretation from the live rules/team.
- **Audit/known-issue novelty:** PARTIALLY RESOLVED. The specific public v4.3.4 OpenZeppelin report is scoped to Permit2Proxy, while NativeOrder whole-balance refund intent is publicly discussed. Other applicable audits or prior disclosures remain possible.
- **Production victim-state prevalence:** OPEN. Local reproduction of a natural partial-fill residual does not establish prevalence on deployed production instances.
- **Reporting deadline:** NOT CLEARED. Evidence of this candidate existed by the September 29, 2026 status snapshot, well before the October 20 recheck. A new information-page timestamp does not restart the 24-hour initial-discovery clock. Do not submit without explicit confirmation that a late report is eligible; the terms make no such guarantee.
- **KYC:** Required for payout.

Decision: **do not submit H-E2 now, and do not run more synthetic variants of the same mechanism.** Preserve the result and all negative/calibration evidence. Reopen only if a genuinely new, externally verifiable fact changes a remaining gate or 1inch explicitly clarifies eligibility.

## 6. Separate technical candidate: H-E1 signature binding

Source:
https://github.com/1inch/limit-order-protocol/blob/4.3.4/contracts/extensions/NativeOrderImpl.sol

Static observation: `isValidSignature` reconstructs the original order from the ERC-1271 signature, derives the deterministic clone address from that order, patches the maker to the clone, and compares the patched hash with the LOP-supplied hash. No simple mismatch-acceptance path is established by the current reading.

Status remains `HYPOTHESIS / NOT TESTED IN THIS RECHECK`. A useful next probe would be a local-only property test that verifies the exact encoding succeeds and single-field mutations/truncated encodings cannot return the ERC-1271 magic value. This should be treated as a falsifiable candidate, not as a suspected vulnerability. If the property passes, preserve it as a negative result and stop pursuing this probe family. If a genuinely new vulnerability is found, record its real first-discovery timestamp; do not reset timestamps to evade the bounty's deadline rule.

## 7. Next action

Because H-E2 is an unreliable payout path under the deadline rule and H-E1 is only an untested validation hypothesis, compare alternative active bounty programs that fit our established Solidity/EVM capabilities and payout constraints before investing another long cycle in 1inch. Prefer exact source/release pins, explicit authorized local testing, clear in-scope impacts, and terms whose reporting eligibility can be met. Do not resume the deferred evidence-layer implementation as part of this research step.

## Sources

- 1inch information page: https://immunefi.com/bug-bounty/1inch-SmartContracts/information/
- 1inch scope page: https://immunefi.com/bug-bounty/1inch-SmartContracts/scope/
- 1inch releases: https://github.com/1inch/limit-order-protocol/releases
- 1inch v4.3.4 source: https://github.com/1inch/limit-order-protocol/tree/4.3.4
- Official audit archive and coverage description: https://github.com/1inch/1inch-audits
- NativeOrder PR/review history: https://github.com/1inch/limit-order-protocol/pull/390
