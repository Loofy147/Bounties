# Case Study — Euler and Wormhole: Transition Closure vs Source Authenticity

**Status:** HISTORICAL CASE STUDY / RESEARCH METHOD  
**Checked:** 2026-10-25  
**Finding status:** No current bounty target or new vulnerability is asserted.

## 1. Executive comparison

Euler V1 and Wormhole's Solana bridge illustrate two distinct invariant failures:

- **Euler — transition-closure failure:** a state-changing operation moved value out of a user's collateral accounting without the health check enforced by related paths. A later liquidation transition monetized the resulting unhealthy state.
- **Wormhole — provenance/authenticity failure:** the bridge parsed attacker-controlled account data as though it were the canonical Instructions sysvar. The data could claim that signature verification had occurred, even though the real Solana secp256k1 verification instruction had not established those signatures.

The shared principle is that a protocol must validate not only the apparent content or local operation, but the invariant-relevant meaning and provenance of the state transition.

This is a taxonomy for reviewing code and evidence, not evidence that a current target contains either issue.

## 2. Euler: what happened, at transaction and call levels

### 2.1 Correct the transaction-count simplification

**ESTABLISHED — Euler's own retrospective:**

The exploit timeline should not be described as exactly six transactions consisting of one deployment, four asset loops, and one exit. Euler's retrospective records this sequence:

1. At 08:50:23 UTC on 2023-03-13, one attacker-controlled address deployed an exploit contract.
2. At 08:50:35 UTC, a second copy of the same exploit contract was deployed by another address.
3. At 08:50:59 UTC, the second address executed the first successful exploit transaction, stealing about $8.8 million in assets.
4. At 08:56:35 UTC, the first address began several more exploit transactions over roughly 15 minutes.
5. Afterward, assets were swapped/consolidated across attacker-controlled addresses. At 10:38 UTC, 100 ETH was sent onward to Tornado Cash.

Euler explains that the early activity was affected by a separate address that front-ran the first planned exploit transaction. Therefore, distinguish exploit-contract deployments, successful exploit transactions, market-level call loops, and later fund movements. They are not interchangeable counts.

Source: [Euler Labs retrospective — “The exploit in real-time”](https://www.euler.finance/blog/war-peace-behind-the-scenes-of-eulers-240m-exploit-recovery).

### 2.2 Markets and source limitations

CertiK's incident analysis enumerates five affected Euler pools: eDAI, eWETH, eWBTC, ewstETH, and eUSDC. Reporting that only DAI, WBTC, USDC, and wstETH were involved omits the eWETH pool.

CertiK's DAI example is transaction **0xc310a0affe2169d1f6feec1c63dbc7f7c62a887fa48795d327d4d2da2d6b111d**:
- [Transaction on Etherscan](https://etherscan.io/tx/0xc310a0affe2169d1f6feec1c63dbc7f7c62a887fa48795d327d4d2da2d6b111d)
- [CertiK incident analysis and the inner-call narrative](https://www.certik.com/blog/euler-finance-incident-analysis)

That transaction is an illustrative DAI trace. Euler's chronology separately explains that the first successful transaction was associated with a different address that front-ran the main attack sequence. Do not treat one example transaction as the complete trace of all attacker-controlled addresses.

### 2.3 One DAI loop — nested calls, not one call per bullet

The DAI transaction's conceptual call structure, supported by CertiK's trace, is:

~~~text
Aave flash loan (DAI)
  └─ attacker callback
       ├─ Euler deposit: DAI -> eDAI collateral
       ├─ Euler mint: increase eToken balance + matching dToken liability
       │    └─ checkLiquidity(account) passes while account is healthy
       ├─ repay part of the debt using retained DAI
       ├─ Euler mint again to scale the leveraged position
       ├─ donateToReserves: reduce account eToken balance
       │    └─ missing post-transition health check
       ├─ attacker-controlled liquidator contract calls liquidate
       │    └─ violator account is now unhealthy
       │         └─ liquidator receives discounted collateral
       ├─ withdraw/transfer collateral proceeds
       └─ repay Aave flash loan plus fee
~~~

The exact quantities and subcall ordering differ by transaction and asset market. The model above captures the invariant-relevant composition; it is not offered as a substitute for the transaction trace.

Important precision:
- **mint()** increases both eToken collateral accounting and dToken debt accounting, and normally checks liquidity after that transition.
- **donateToReserves()** reduces the caller's eToken balance and raises reserves, but the vulnerable implementation omitted the corresponding liquidity check.
- Euler's retrospective calls the result “self-liquidation,” but CertiK's source-level example distinguishes the **violator** contract from a separate **liquidator** contract controlled by the same attacker. This is self-liquidation in the control/economic sense, not the same Euler account acting as both parties.
- The flash loan supplies temporary working capital and constrains execution atomically; it is not the root cause. The missing health check and liquidation accounting are the security failure.

Sources:
- [Euler Labs retrospective](https://www.euler.finance/blog/war-peace-behind-the-scenes-of-eulers-240m-exploit-recovery)
- [CertiK trace](https://www.certik.com/blog/euler-finance-incident-analysis)
- [eIP-14 governance proposal](https://forum.euler.finance/t/eip-14-contract-upgrades/305)

### 2.4 Root cause and repair evidence

**ESTABLISHED:** Euler states that donateToReserves was introduced as part of a fix to a first-depositor issue, was sent for audit, and omitted a health check that would stop a user from making an already-indebted account unhealthy simply by donating collateral. Thus, “it was never audited” is contradicted by the official retrospective.

The logical defense is to enforce the correct postcondition after the donation mutation, such as calling checkLiquidity(account) in the relevant implementation, subject to the protocol's intended semantics.

**Provenance caution:** A public proposal exists at [Euler legacy repository PR #199](https://github.com/euler-legacy-xyz/euler-contracts/pull/199) titled “add: check liquidity in EToken::donateToReserves()”; its displayed patch adds checkLiquidity(account) before logging status. The public PR is marked open/unmerged by GitHub, and the archived legacy master source read on 2026-10-25 still does not contain that call in donateToReserves. Therefore, do **not** cite PR #199 as proof that this exact patch was merged or deployed in production. It is useful as an illustrative minimal logic change, not as deployment provenance.

The target's deployed remediation history is outside the scope of this case note and must be separately source-verified before making claims about the final production patch.

## 3. Wormhole: a data-provenance check failure

### 3.1 Security boundary

Wormhole's Solana verify_signatures procedure reads the prior top-level instruction through the Instructions sysvar to connect the claimed secp256k1 signature-verification result to the VAA body hash and current Guardian set.

The vulnerability was not adequately described as “the verifier forgot to check the program ID of the instruction.” The key failure was trusting account data supplied in the account list without first proving the account was the canonical Instructions sysvar. An attacker could supply a fake account with data serialized to look like an instruction history. A check on a parsed instruction's apparent program ID alone does not authenticate the source account from which the data came.

### 3.2 Transaction-level shape

Conceptually, the malicious Solana transaction supplied a fake instructions-sysvar account whose data described a crafted prior secp256k1-style instruction. Wormhole then consumed that false history as evidence of signature verification, accepted the forged guardian-signature state, posted/recorded the VAA, and allowed the Solana-side bridge representation to mint 120,000 wETH without valid Guardian authorization. This unbacked representation could then be used to redeem assets through the bridge.

This is a provenance violation: **the parsed contents looked structurally acceptable, but their source was not the trusted sysvar account**.

Sources:
- [Wormhole's fix commit e8b91810a9bb35c3c139f86b4d0795432d647305](https://github.com/wormhole-foundation/wormhole/commit/e8b91810a9bb35c3c139f86b4d0795432d647305)
- [Wormhole's current Solana verify_signature.rs](https://github.com/wormhole-foundation/wormhole/blob/main/solana/bridge/program/src/api/verify_signature.rs)
- [Wormhole's Solana Core Contract docs](https://docs.wormhole.com/products/messaging/reference/core-contract-solana/)
- [Solana's official instruction-introspection documentation](https://solana.com/docs/core/instructions/instruction-introspection)

### 3.3 Patch diff and defense in depth

The verified Wormhole commit **e8b91810a9bb35c3c139f86b4d0795432d647305**, titled “Check instructions sysvar,” adds this guard at the start of verify_signatures:

~~~rust
if *accs.instruction_acc.key != solana_program::sysvar::instructions::id() {
    return Err(SolitaireError::InvalidSysvar(*accs.instruction_acc.key));
}
~~~

The change is four added source lines in the official commit diff. The current source additionally uses load_current_index_checked and load_instruction_at_checked, and then separately checks that the loaded instruction's program_id is the secp256k1 program. These checks defend different properties:

1. **Account provenance:** the supplied account is the canonical Instructions sysvar.
2. **Instruction identity:** the prior instruction is actually the expected secp256k1 verification program.
3. **Message binding:** the parsed signature instruction references the expected message/hash and signature data.
4. **Guardian binding:** the accepted signer indices correspond to the currently valid Guardian set.

No one of these is a substitute for the others.

## 4. Cross-case taxonomy

| Dimension | Euler V1 | Wormhole Solana bridge |
|---|---|---|
| Primary invariant | Account health / collateral-debt safety after mutation | Authenticity and provenance of signature-verification evidence |
| Fault class | Missing post-transition validation | Missing validation of the source account; unchecked deserialization |
| Exploit composition | Deposit/mint leverage → collateral donation → liquidation → withdrawals | Fake sysvar data → forged verification state → VAA acceptance → unbacked mint/redemption |
| Security layer | Economic state machine and accounting | Cross-program data provenance and cryptographic authorization |
| Why isolated review can miss it | Donation is legitimate in normal use; danger appears with later liquidation | Parsed instruction data can look valid; danger appears if the data's source is not authenticated |
| Primary prevention | State invariant coverage across every relevant mutator and downstream transition | Verify canonical sysvar identity and independently verify instruction ID/message/signer linkage |
| Useful test property | Every allowed sequence preserves the protocol's specified health and accounting rules | Replacing the canonical sysvar with an arbitrary account must always fail |
| Required evidence | Target-pinned state transition, economic impact, independent rerun | Target-pinned account-identity negative test plus proof that invalid source data cannot authorize a VAA |

**INFERENCE:** These cases motivate a generalized review rule:

> Every security-sensitive value must have both a valid semantic interpretation and an authenticated provenance path, and every mutation must preserve the relevant postcondition across downstream operations.

## 5. Turning the lesson into an executable research test

For a new, authorized target, do not start with “find the missing check.” Start by specifying a falsifiable property.

### Transition-closure test (Euler-like)

- Enumerate all functions that can change collateral, debt, share balance, reserves, withdrawal capacity, or liquidation eligibility.
- For each, record the precondition, state mutation, postcondition check, and next operation that consumes the resulting state.
- Build a locally reachable baseline state through the protocol's own functions.
- Test a bounded sequence of permitted operations; observe the full before/after accounting state.
- Add healthy-state and authorization-denied negative controls.
- Apply a test-oracle mutation that removes the intended invariant and verify that the test fails.
- Measure victim loss, protocol loss, actor receipts, and all costs separately.
- Only then evaluate current program scope, known issues, novelty, first-discovery time, and eligibility.

### Provenance-validation test (Wormhole-like)

- Enumerate every externally supplied account/object that the protocol treats as trusted execution context or verification evidence.
- Identify the canonical identity predicate for the object (for Solana, the exact sysvar key and expected owning/source rules where applicable).
- Test that an arbitrary account containing structurally plausible data is rejected.
- Independently test the loaded instruction's program ID and the binding of message/hash/signers.
- Preserve distinct negative tests per trust condition, so a failure identifies which validation layer is missing.

These are test specifications for a new, scope-approved target, not instructions to probe live production systems.

## 6. Evidence labels

- **ESTABLISHED:** Historical Euler and Wormhole failures and the referenced source changes are documented in the cited primary sources.
- **EXPERIMENTALLY_SUPPORTED:** This note performs no local reproduction. No new experiment was run.
- **INFERENCE:** Transition-closure and provenance-validation reviews are reusable methods suggested by the cases.
- **HYPOTHESIS:** A current target could contain an analogous fault; this requires target-specific evidence.
- **UNKNOWN:** Whether any current bounty target contains such a fault, whether it is novel/in scope, and the precise deployed remediation state of Euler V1 from PR #199 alone.

## 7. Source register — checked 2026-10-25

1. Euler Labs, [“War & Peace: Behind the Scenes of Euler’s $240M Exploit Recovery”](https://www.euler.finance/blog/war-peace-behind-the-scenes-of-eulers-240m-exploit-recovery), published 2024-01-10.
2. Euler Governance Forum, [“eIP 14: Contract Upgrades”](https://forum.euler.finance/t/eip-14-contract-upgrades/305), 2022-07-06.
3. CertiK, [“Euler Finance Incident Analysis”](https://www.certik.com/blog/euler-finance-incident-analysis), 2023-03-13. Used for the illustrated DAI transaction and distinct violator/liquidator contract roles; secondary source.
4. Euler legacy repository, [EToken.sol](https://github.com/euler-legacy-xyz/euler-contracts/blob/master/contracts/modules/EToken.sol), and [PR #199](https://github.com/euler-legacy-xyz/euler-contracts/pull/199). Used to distinguish illustrative patch logic from a merged/deployed patch claim.
5. Wormhole Foundation, [commit e8b91810a9bb35c3c139f86b4d0795432d647305](https://github.com/wormhole-foundation/wormhole/commit/e8b91810a9bb35c3c139f86b4d0795432d647305), “Check instructions sysvar.”
6. Wormhole Foundation, [Solana verify_signature.rs](https://github.com/wormhole-foundation/wormhole/blob/main/solana/bridge/program/src/api/verify_signature.rs).
7. Wormhole, [Solana Core Contract docs](https://docs.wormhole.com/products/messaging/reference/core-contract-solana/).
8. Solana, [Instruction Introspection](https://solana.com/docs/core/instructions/instruction-introspection).

This case study does not alter the status of any existing bounty hypothesis and must not be cited as vulnerability evidence against an unrelated target.
