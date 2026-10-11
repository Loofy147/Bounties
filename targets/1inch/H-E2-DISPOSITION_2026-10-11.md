# H-E2 / K-04 — Eligibility and Production Disposition

Snapshot: 2026-10-11
Target: 1inch Limit Order Protocol 4.3.4
Target commit: 7da29889efa2e635611e1caf60f85f595ff7f05f
Branch: research/b0-1inch-external-gates-2026-10-08

## Decision summary

Do not promote H-E2 to IN-SCOPE or SUBMISSION-READY.

The local behavior remains experimentally supported. Evidence now shows that the underlying residual-balance state exists in production, but the complete passive resolver-cancellation event history contains no observed positive resolver reward. The current program page also contains a 24-hour initial-discovery reporting rule. Since H-E2 was already documented as an open hypothesis in the 2026-09-29 research snapshot, reward eligibility is materially at risk if that rule applied when the hypothesis was discovered.

This is an eligibility/reachability disposition, not proof that the code path is impossible or that no vulnerability exists.

## 1. Target version status

GitHub's current tag refs contain these stable 4.x line versions:

- 4.3.0
- 4.3.1
- 4.3.2
- 4.3.4

The highest stable semantic version tag observed on 2026-10-11 is 4.3.4, resolving to tag object 0a40e01befff19d925457b55191900fb456c2dd and target commit 7da29889efa2e635611e1caf60f85f595ff7f05f.

This supports continued use of the pinned 4.3.4 snapshot for research, subject to the program's exact latest-tag/release rule and any project-side scope interpretation.

## 2. Official audit archive: exact and adjacent coverage

The official 1inch audit archive README identifies the v4.3.4 OpenZeppelin review as:

"The Permit2Proxy extension for the Limit Order Protocol — a simpler Permit2 integration without witness data, used to transfer maker and taker assets via Permit2 signature transfers."

The archive also lists historical Limit Order Protocol v4 and v4.1 reports. No report in the archive's path/description inventory is explicitly named NativeOrderFactory or NativeOrderImpl.

Result:

- ESTABLISHED: there is a dedicated v4.3.4 Permit2Proxy report.
- NOT ESTABLISHED: that report covers NativeOrderFactory/NativeOrderImpl.
- NOT ESTABLISHED: historical v4/v4.1 PDFs cover the later NativeOrder extension.
- OPEN: full report-body and known-issue reconciliation is still required before any claim of novelty.

Primary archive:
https://github.com/1inch/1inch-audits/blob/master/README.md

## 3. Public design discussion and adjacent issue

### PR #390 — native order design

On 2025-09-24, reviewers directly asked whether cancellation should send the entire contract WETH balance to the maker, including accidentally sent WETH.

The implementation author answered that this was intentional because WETH can remain in the contract after a cross-chain order cancellation and should be returned to the maker. The same reply notes the maker's ability to use the `withdraw` function to withdraw WETH.

PR:
https://github.com/1inch/limit-order-protocol/pull/390

Interpretation:
- The aggregate-balance return policy is explicitly discussed and intentional.
- This is adjacent to H-E2, not proof that the particular positive-resolver-reward haircut interaction was recognized or accepted.

### PR #422 — cancelled-order WETH allowance

PR #422 proposed setting WETH allowance to zero after cancellation and included a regression test that a cancelled order cannot be refilled using WETH accidentally deposited afterward. The PR is closed and unmerged; the discussion includes the maintainer statement, "No need for all users to pay for a potential mistake of one user".

PR:
https://github.com/1inch/limit-order-protocol/pull/422

Interpretation:
- This is a public adjacent discussion about cancelled orders, leftover/accidentally deposited WETH, and post-cancellation behavior.
- It is not the same as H-E2, which concerns the resolver reward being subtracted from the full WETH balance during resolver cancellation.
- Treat it as relevant prior art and a novelty caveat, not as a proven duplicate.

## 4. Complete passive event scan — Ethereum mainnet

The event signature was verified against a live resolver-cancellation receipt:

`NativeOrderCancelledByResolver(bytes32,uint256,uint256)`
topic0: `0x22770c588cf5c5f476664dc9b7c78816ad26f3d653e290d5a4f0053f015ae9ea`

Passive logs were queried by topic0 from the NativeOrderFactory deployment window through the latest Etherscan block returned during the check. The query used two block windows due to API result-window limits.

Window A:
- blocks 23,447,660–26,000,000
- 6,337 matching events
- first matching event: block 23,455,255
- last matching event in window: block 25,999,337

Window B:
- blocks 26,000,001–latest
- 364 matching events
- latest matching event: block 26,167,845

Combined:
- 6,701 matching events
- 0 malformed event data records
- 6,701 decoded records with resolverReward = 0
- 0 observed records with resolverReward > 0

This is a passive signature-wide query on Ethereum mainnet; it does not represent an emitter-address allowlist, and it does not establish what resolvers might do under other conditions. It establishes that no non-zero resolver reward was observed in the queried event history up to the latest block returned.

Interpretation:
- A production non-zero reward example is currently UNKNOWN / not observed.
- The absence of a positive event does not disprove the local state transition: callers may use rewardLimit=0 or otherwise never enter the rewardable path.
- It does mean passive production evidence presently fails to corroborate real-world use of the key H-E2 reward branch.

## 5. Confirmed production residual state

Example clone:
`0xb3eea3d5e2ef2728e40f9783fc781bf21f2de58f`

Passive chain evidence:
- Creation block 25,365,981: 4.0 ETH sent to the clone and wrapped.
- Subsequent WETH transfers out: 2.0, 0.2, and 0.45 WETH; total 2.65 WETH.
- Immediately before resolver cancellation, the implied WETH residual was 1.35 WETH.
- Resolver cancellation at block 25,366,005 emitted balance = 1.35 ETH-equivalent and resolverReward = 0.
- The cancellation transaction transferred 1.35 ETH-equivalent to the maker recipient.

Transaction:
https://etherscan.io/tx/0x9d6db312e6e58187b8f3c9da6e78c2a9545230b2b94413570db209a6e1a136a1

This demonstrates a real production residual balance and ordinary refund path. Because the full order-fill calldata/call graph was not decoded in this step, it is recorded as production residual-state evidence, not a complete proof of the semantic classification of each prior transfer.

## 6. Current reporting-rule eligibility risk

The current Immunefi information page (observed 2026-10-11; page says last updated 2026-10-09) says:

"Any vulnerability discovered must be reported no later than 24 hours after the initial discovery. Reports submitted after this window may be considered at 1inch's discretion but are not guaranteed eligibility for a reward."

The same page sets the current smart-contract rewards in USDC on Ethereum:
- Critical: 10% of directly affected mainnet funds, $30,000 minimum and $500,000 maximum.
- High: $10,000–$30,000.
- Medium: $2,000–$10,000.
- Low: $100–$2,000.

Primary source:
https://immunefi.com/bug-bounty/1inch-SmartContracts/information/

The existing research record already lists H-E2 as a hypothesis on 2026-09-29. If the 24-hour clause applied in the same form at that time, a submission now would be outside the normal window; the page only allows discretionary consideration, not guaranteed eligibility. The exact historical effective date of this wording has not been established in this research record.

Decision:
- Do not label bounty eligibility as cleared.
- Do not misstate the initial-discovery date.
- If external submission is later considered, first obtain a clear program ruling on the 24-hour rule and resolver-role eligibility.
- No external submission was made.

## 7. Final state

| Claim / gate | Status |
|---|---|
| 4.3.4 is highest stable tag observed | ESTABLISHED for observed tag refs |
| Factory source matches pinned source | ESTABLISHED |
| Resolver-reward source semantics | ESTABLISHED |
| Local H-E2 behavior | EXPERIMENTALLY_SUPPORTED |
| Production residual state exists | EXPERIMENTALLY_SUPPORTED by passive chain evidence |
| Production non-zero resolver reward exists | UNKNOWN; none observed in 6,701 events |
| v4.3.4 report covers NativeOrder | UNKNOWN / not established |
| Adjacent prior art | ESTABLISHED (PR #390, PR #422) |
| Novelty | OPEN |
| Resolver-role eligibility | OPEN |
| 24-hour reporting-window eligibility | AT RISK / historic rule effective date unresolved |
| Overall bounty finding | HYPOTHESIS; not submission-ready |

## 8. Stop rule

Stop generating synthetic H-E2 variants. The next useful work is not another local reproduction; it is a bounded decision on whether to retain H-E2 only as a technical research case or seek a program eligibility clarification. The existing record is not sufficient for a defensible bounty submission.

### Event-emitter validation

To validate that the signature-wide event sample corresponds to NativeOrder clones, three distinct event-emitter addresses were checked through their Ethereum internal-transaction traces. Each was created via `CREATE2` by the recorded NativeOrderFactory address `0xe12E0f117d23a5ccc57f8935CD8c4E80cD91FF01` and immediately deposited WETH during creation. The sample emitters include addresses from both searched block windows.

This spot-check supports the event-class attribution. It does not claim that every emitter was individually traced; the 6,701 count remains an event-signature query.
