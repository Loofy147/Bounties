# SSV v2.0.0 — EB deviation lifecycle review v0.1

**Status:** HYPOTHESIS KILLED AT SOURCE/MODEL LEVEL; not a Solidity test result.  
**Scope pin:** ssvlabs/ssv-network@v2.0.0, commit 9bb7b21d4432f34f623bed3e0bb3fa77f1e5d2b9.

## Question

Does a missing or stale deviationSettled flag cause deviation values to be omitted or subtracted twice after liquidate → reactivate → EB change → remove/liquidate, possibly across clusters sharing an operator?

## Source facts

### 1. No deviationSettled state exists in the reviewed implementation

SSVClusters.sol, SSVValidators.sol and the relevant EB storage source do not use a deviationSettled flag. Accounting is derived from existing state:

- cluster.active and cluster.validatorCount determine whether baseline validator counts are active;
- clusterEB[clusterId].vUnits stores the last explicit EB snapshot (zero means implicit/baseline EB for these calculations);
- operatorEthVUnits and daoTotalEthVUnits store aggregate deviations;
- ethSnapshot.block == 0 excludes removed/uninitialized operators from active operator-deviation updates.

The proposed “settlement flag is not reset” mechanism is therefore CONTRADICTED for this source pin. A distinct state-corruption mechanism must be identified before a vulnerability claim is warranted.

### 2. Liquidation removes the active deviation while retaining the snapshot

In SSVClusters._executeLiquidation:

1. sp.updateDAO(false, cluster.validatorCount) reduces the active baseline count.
2. It reads ebSnapshot.vUnits, computes the deviation relative to validatorCount * BPS_DENOMINATOR, and removes that deviation from DAO and active operators.
3. It marks the cluster inactive and clears its balance/index fields.
4. It does not zero ebSnapshot.vUnits; reactivate uses the retained snapshot to restore effective-vUnits accounting.

Source: [SSVClusters.sol](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/contracts/modules/SSVClusters.sol#L555-L616).

### 3. Reactivation re-adds deviation from the snapshot

reactivate computes:

    vUnitsCluster = clusterEB[clusterId].vUnits
    baselineVUnits = validatorCount * BPS_DENOMINATOR
    effectiveVUnits = vUnitsCluster > 0 ? vUnitsCluster : baselineVUnits
    clusterDeviation = max(vUnitsCluster - baselineVUnits, 0)

It passes clusterDeviation to OperatorLib.updateClusterOperatorsOnReactivation, increments DAO's active validator baseline, and adds the same cluster deviation to daoTotalEthVUnits. No lifecycle flag is read.

Sources: [reactivate](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/contracts/modules/SSVClusters.sol#L129-L177), [OperatorLib.updateClusterOperatorsOnReactivation](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/contracts/libraries/OperatorLib.sol#L250-L330).

### 4. Removal distinguishes active from already-liquidated clusters

For the ETH version, _bulkRemoveValidator updates active operator/DAO baseline counts only if cluster.active; it then decrements cluster.validatorCount. If EB tracking is explicit, it subtracts validatorsRemoved * BPS_DENOMINATOR from the snapshot. When the cluster becomes empty:

- if it was active, residual snapshot deviation is subtracted from active operators and DAO;
- if it was already liquidated, it skips the global decrement because liquidation already removed that deviation;
- it clears the EB snapshot in either case.

Source: [SSVValidators.sol](https://github.com/ssvlabs/ssv-network/blob/v2.0.0/contracts/modules/SSVValidators.sol#L178-L254).

## Counter-evidence and duplicate gate

Public SSV [PR #629](https://github.com/ssvlabs/ssv-network/pull/629), closed without merge on 2026-09-02, describes a deterministic endpoint identity after:

    register → EB-up to 64 ETH → liquidate → reactivate → EB-down to 32 ETH baseline

The PR states its local Hardhat test passed and no issue was found at the pinned 9bb7b21d commit. The test does not include every proposed reactivate → remove variation, but it is strong counter-evidence to treating the general lifecycle cycle as novel.

The current Immunefi terms exclude issues documented in audit reports and in project docs/branches. A report must not merely restate SSV-8 or the PR #629 lifecycle invariant.

## Reference-model outcomes

The dependency-free model at research/ssv-v2-transition-model/ asserts that:

- liquidation removes active baseline/deviation accounting but leaves the snapshot available;
- reactivation restores the same effective-vUnits aggregate;
- removing the final validator after liquidation does not subtract global deviation twice;
- removing the final validator after reactivation clears the restored deviation once;
- EB updates after reactivation adjust deviations before removal;
- a second cluster sharing an operator is unchanged by the first cluster's liquidate/reactivate cycle;
- repeated cycles return to the same accounting endpoint.

Six lifecycle tests pass. This is an abstract model, not target Solidity execution.

## Decision

Do not report the deviationSettled hypothesis. It is contradicted as phrased, and the general endpoint identity is already publicly documented/tested in PR #629. Any remaining work must compare protocol totals against independently recomputed active-cluster exposure, not only compare two contract-maintained aggregates, and must target the exact current runtime hashes.
