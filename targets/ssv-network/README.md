# SSV Network v2.0.0 — bounty research dossier

**Snapshot date:** 2026-10-25  
**Repository target:** [ssvlabs/ssv-network](https://github.com/ssvlabs/ssv-network)  
**Bounty:** [Immunefi — SSV Network](https://immunefi.com/bug-bounty/ssvnetwork/information/)  
**Status:** RECONNAISSANCE; no vulnerability claim; no report-ready candidate.

## Decision

Do not advance the proposed deviationSettled lifecycle-contamination hypothesis or the cSSV transfer-hook hypotheses to a bounty candidate on current evidence. Source inspection contradicts the named flag hypothesis; the accounting model preserves aggregate exposure across the reviewed lifecycle; public SSV PR #629 independently describes and reports a passing test for the key EB-up → liquidate → reactivate → EB-down cycle (closed, not merged). The transferFrom concern is contradicted by source call order: allowance is spent first, but the hook runs before ERC20 balances are mutated and computes settlement from pre-transfer balances.

This does **not** prove the entire SSV v2.0.0 system secure. These leads are not reproducible findings and must not be promoted merely because a test name is missing.

## Evidence ledger

| Claim | Label | Result |
|---|---|---|
| deviationSettled exists in the reviewed v2.0.0 lifecycle | CONTRADICTED | No such state variable was found in inspected SSVClusters.sol, SSVValidators.sol, or the relevant storage model. Accounting derives from active state, validator count, EB snapshot and aggregate deviations. |
| Liquidation removes active baseline/deviation accounting but retains EB snapshot for reactivation | ESTABLISHED | _executeLiquidation removes active deviation; reactivate restores it using the retained snapshot. |
| Removing the final validator after liquidation avoids a second global deviation subtraction | ESTABLISHED | The ETH remove path only subtracts the residual global deviation if the cluster was active; it clears the snapshot in either case. |
| The lifecycle hypothesis is novel and bounty-eligible | CONTRADICTED / UNKNOWN | Public PR #629 describes a passing test for the central round-trip identity. Immunefi also excludes issues documented in audits/docs/branches. |
| transferFrom can make the hook settle from a post-transfer balance | CONTRADICTED | Allowance changes do not mutate token balances; _beforeTokenTransfer and the staking callback execute before the transfer's balance mutations. |
| Same-accumulator multi-hop transfers erase intermediate rewards | NOT REPRODUCED | The reference model preserves the reward amounts settled at each transfer boundary. |
| One-wei cSSV makes dust permanently lost | CONTRADICTED as stated | Claim rounding may defer a sub-100,000-wei payout; with a nonzero cSSV balance, accrued dust can accumulate with later rewards. |
| Permissionless syncFees before transfer creates protocol loss | NOT SUPPORTED | The hook calls _syncFees itself; no distinct loss mechanism was established. |

## Source pins

- Release tag v2.0.0, commit [9bb7b21d4432f34f623bed3e0bb3fa77f1e5d2b9](https://github.com/ssvlabs/ssv-network/releases/tag/v2.0.0).
- [SSVClusters: reactivate](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/contracts/modules/SSVClusters.sol#L129-L177), [EB update](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/contracts/modules/SSVClusters.sol#L369-L430), [liquidation](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/contracts/modules/SSVClusters.sol#L555-L616).
- [SSVValidators: removal path](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/contracts/modules/SSVValidators.sol#L153-L264).
- [CSSVToken pre-transfer hook](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/contracts/token/CSSVToken.sol#L26-L39).
- [SSVStaking requestUnstake](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/contracts/modules/SSVStaking.sol#L65-L92), [onCSSVTransfer and settlement](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/contracts/modules/SSVStaking.sol#L173-L228).
- Existing tests: [reactivate](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/test/unit/SSVClusters/reactivate.test.ts), [liquidate](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/test/unit/SSVClusters/liquidate.test.ts), [hook unit tests](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/test/unit/SSVStaking/onCSSVTransfer.test.ts), [transfer E2E tests](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/test/e2e/staking/staking-transfers.test.ts), [unstake tests](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/test/unit/SSVStaking/requestUnstake.test.ts).
- Public lifecycle counter-evidence: [SSV PR #629](https://github.com/ssvlabs/ssv-network/pull/629), closed without merge on 2026-09-02; its description says the local Hardhat lifecycle test passed and no issue was found at the pinned main commit.
- Official stale-snapshot emergency fix notice: [SSV Governance, 2026-05-07](https://forum.ssv.network/t/publication-of-the-use-of-the-multi-sig-emergency-powers-on-the-6th-of-may-2026/2127); records updated SSVClusters and SSVValidators module pointers via [the transaction](https://etherscan.io/tx/0x3fdb778cb6a404b1c38271c58d2d9a001cd8dc97feee27ddc87376d93fb4c30c).
- [Immunefi program terms](https://immunefi.com/bug-bounty/ssvnetwork/information/): audit/docs/branch exclusions apply, PoC required, production/public-testnet testing prohibited.

## Deployment identity warning

The v2.0.0 tag is a source snapshot, not a sufficient identifier for today's deployed implementation. The checked-in mainnet deployment attestation inspected during this review was generated on 2026-04-19, before the 2026-05-06 emergency patch. The official announcement confirms two module pointers were updated, but this review did not independently re-query and compare all nine current implementation runtime hashes. The mapping “current proxy → implementation → runtime hash → source commit” remains UNKNOWN. Do not treat either the release tag or the stale attestation as proof of current production bytecode.

## Local reference-model validation

research/ssv-v2-transition-model/ contains dependency-free Python models for the high-level vUnits lifecycle and cSSV settlement ordering. They do not execute Solidity or establish deployed-contract behavior.

Run:

    cd research/ssv-v2-transition-model
    python -m unittest -v

Local outcome at this snapshot: **11/11 tests passed**. These prove the model's stated rules only.

## Next discriminating step

If pursuing SSV further, pin all nine current mainnet runtime hashes to exact source. Then run any genuinely new candidate sequence against a local Hardhat fork or the project's own harness. Do not submit the current leads as vulnerabilities. A coverage gap is not an invariant violation.
