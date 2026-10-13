# Enzyme Onyx — SyncRedeemHandler Initial Triage

**Run date:** 2026-10-13  
**Research branch:** `bounty/enzyme-onyx-sync-redeem-handler`  
**Baseline branch:** `feat/reentrancy-lab`  
**Run status:** source-pinned reconnaissance and static triage only  
**Finding status:** no vulnerability established; no report submitted

## 1. Program and target snapshot

- **Program:** [Enzyme Onyx on Immunefi](https://immunefi.com/bug-bounty/enzyme-onyx/information/)
- **Scope page:** https://immunefi.com/bug-bounty/enzyme-onyx/scope/
- **Target added to official scope:** 2026-10-12
- **Target:** [SyncRedeemHandler.sol](https://github.com/enzymefinance/protocol-onyx/blob/d8a522d6ca58af9dbb831dad2b8045a88952e468/src/components/issuance/redeem-handlers/SyncRedeemHandler.sol)
- **Pinned source commit:** `d8a522d6ca58af9dbb831dad2b8045a88952e468`
- **Pinned source blob SHA:** `8e90babe79714f66728111406e35ddd3b7442aa4`
- **Official program page last updated:** 2026-10-12; the current scope page reports 46 in-scope assets.
- **Reward:** paid in USDC on Ethereum. Critical: $20,000–$200,000, calculated as 10% of directly affected funds subject to the $200,000 cap and $20,000 minimum. High: $5,000–$20,000. Medium: $1,000–$5,000.
- **KYC:** not required for payout processing.

The baseline documents `research/BUG-HUNTER-FOUNDATION-v0.1.md` and `CURRENT_STATUS_2026-09-29.md` were read on `feat/reentrancy-lab`. The existing 1inch research endpoint remains separate; this run does not revise that track.

## 2. Scope contract

**Established from the live Immunefi information/scope pages:**

1. Every severity requires a complete, reproducible PoC. Accepted PoC environments are a fork of the live deployment or deployed contracts running actual production code. Mock-only, heavily modified, hypothetical, or partial demonstrations are not acceptable.
2. No testing against mainnet or public-testnet deployed code. Perform permitted execution only in an isolated local fork.
3. Testing with pricing oracles or third-party smart contracts is prohibited. Keep experiments bounded to authorized Enzyme-owned components and do not involve third-party integrations.
4. No denial-of-service against project assets, high-traffic automated testing, social engineering, or public disclosure of an unpatched issue.
5. The program excludes issues already recorded in the applicable risk/limitation documents and audit reports, user/configuration error, unrealistic fund states, and the published default exclusions.

Official source: [Immunefi scope and rules](https://immunefi.com/bug-bounty/enzyme-onyx/scope/) and [program information/rewards](https://immunefi.com/bug-bounty/enzyme-onyx/information/).

## 3. Target behavior model

At the pinned source, `redeem(_sharesAmount)`:

1. rejects a zero share amount;
2. reads the cached share price and timestamp, then applies the configured staleness limit;
3. asks the configured FeeHandler to settle an exit fee against gross shares;
4. prices the remaining shares and converts the value to the configured redemption asset;
5. rejects a zero asset payout;
6. burns the caller's gross shares through the registered Shares redeem-handler boundary;
7. transfers the computed assets to the caller; and
8. calls the optional post-redeem hook, then emits the redemption event.

Related source inspected at the same commit: `ValuationHandler.sol`, `FeeHandler.sol`, `Shares.sol`, `ComponentHelpersMixin.sol`, `ValueHelpersLib.sol`, and the post-redeem hook interface. This is a static source read, not a runtime reproduction.

## 4. Novelty and exclusion gate

The target repository contains [ChainSecurity QA notes for SyncRedeemHandler](https://github.com/enzymefinance/protocol-onyx/blob/d8a522d6ca58af9dbb831dad2b8045a88952e468/audits/QA/ChainSecurity_QA_EnzymeFoundation_SyncRedeemHandler.md). The program's exclusion of documented audit/risk items means the following are **not bounty candidates from this run**: cached/stale share-price effects and round trips; administrator-set asset-rate mispricing; known share/asset/fee rounding; insufficient-liquidity or configuration-driven redemption DoS; privileged configuration/access-control failures; the documented compliance-hook/transfer-validator behavior; zero-share-value/unrealistic fund states; initialization/configuration order; and the pre-existing exit-fee rounding note.

Do not repackage these known points as a new finding. Any future hypothesis must identify a materially different behavior and survive comparison against the entire applicable audit/risk corpus before any report is drafted.

## 5. Initial hypothesis ledger

| ID | Hypothesis / property | Current disposition | Evidence and next discriminating test |
|---|---|---|---|
| SR-01 | Fee calculation could return more fee shares than gross shares, breaking the net-share subtraction. | **Not substantiated; static path appears bounded.** | Pinned `FeeHandler.setExitFee` requires `feeBps < 10,000`; calculation is `grossShares * feeBps / 10,000`. Confirm with a project-code regression/property test in an authorized local environment. |
| SR-02 | Re-entry during payout could redeem the same shares twice. | **Not substantiated.** | The handler burns gross shares before the payout transfer. Re-entry via a non-standard callback token conflicts with the QA trust assumption for the redemption asset (standard ERC-20, no callbacks). Do not use an out-of-assumption token as a bounty PoC. A different, in-scope callback path would need to be demonstrated. |
| SR-03 | The post-redeem hook could be used to bypass redemption constraints. | **Known-risk/exclusion gate.** | The QA report explicitly discusses compliance-hook configuration and ordering. The hook is administrator-configured and invoked after the burn and payout in the same atomic transaction. Do not submit the documented bypass or treat a privileged misconfiguration as attacker capability. |
| SR-04 | A future share-price timestamp could trigger subtraction underflow or a redemption DoS. | **Open hypothesis; no attacker-controlled path identified.** | The inspected `ValuationHandler` stores the timestamp as `uint40(block.timestamp)` during share-value updates. Need an in-scope, non-privileged path to a future timestamp before this becomes a meaningful hypothesis. |
| SR-05 | A failing asset transfer or hook could leave shares burned without payout. | **No inconsistency identified statically.** | The burn, transfer, hook, and event are within one EVM transaction; a revert rolls back earlier state changes. Validate only if a concrete path contradicts the atomicity assumption. |
| SR-06 | Fee settlement and payout use inconsistent prices/rates during one redemption. | **Not substantiated; overlap risk must be excluded.** | Calls inspected are transaction-local, and valuation/rate reads are view calls. Admin-set rates and share-price staleness risks are already covered in the QA report. A novel, attacker-reachable state change during the call would be required. |

**Current conclusion:** no candidate has reached `REPRODUCED`, `IN-SCOPE`, or `SUBMISSION-READY`. No exploitability or vulnerability claim is made.

## 6. Execution record and next gate

- **Acquisition:** GitHub source returned for the pinned commit; source blob SHA recorded above.
- **Local runtime tests:** not run. An attempted repository clone failed because this execution environment could not resolve `github.com`; this is an environment/network limitation, not a target-test failure.
- **Static review:** completed for the target function and its directly called Enzyme components; no confirmed security violation found.
- **Required before promotion:** retrieve/verify a complete local source snapshot and dependencies; reconcile all applicable audit/known-issue material; identify one new attacker-reachable invariant violation; reproduce against the actual production code in the program-authorized local fork; collect state-delta/trace evidence; independently validate impact and novelty; then request human approval before submission.

Evidence path: official Immunefi pages and pinned GitHub source URLs above. No tests were run against live networks or third-party contracts.
