"""Small deterministic reference models for SSV v2 review questions.

These models are specification aids only. They do not execute Solidity, model every
SSV storage invariant, or establish deployed-contract behavior.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

BPS_DENOMINATOR = 10_000
PRECISION = 10**18
ETH_DEDUCTED_DIGITS = 100_000


@dataclass
class Cluster:
    cluster_id: str
    operator_ids: tuple[int, ...]
    validator_count: int
    active: bool = True
    eb_vunits: int = 0  # zero means implicit/baseline EB
    balance: int = 1

    def baseline(self) -> int:
        return self.validator_count * BPS_DENOMINATOR

    def effective_vunits(self) -> int:
        return self.eb_vunits if self.eb_vunits > 0 else self.baseline()


class EBAccountingModel:
    """Mirror the reviewed high-level vUnits lifecycle for active ETH clusters."""

    def __init__(self) -> None:
        self.clusters: dict[str, Cluster] = {}
        self.operator_validator_count: dict[int, int] = {}
        self.operator_deviation: dict[int, int] = {}
        self.dao_validator_count = 0
        self.dao_deviation = 0

    def _apply_operator_count(self, operator_ids: Iterable[int], delta: int) -> None:
        for operator_id in operator_ids:
            next_count = self.operator_validator_count.get(operator_id, 0) + delta
            if next_count < 0:
                raise AssertionError("operator validator count underflow in reference model")
            self.operator_validator_count[operator_id] = next_count

    def _apply_deviation(self, operator_ids: Iterable[int], delta: int) -> None:
        for operator_id in operator_ids:
            next_value = self.operator_deviation.get(operator_id, 0) + delta
            if next_value < 0:
                raise AssertionError("operator deviation underflow in reference model")
            self.operator_deviation[operator_id] = next_value
        self.dao_deviation += delta
        if self.dao_deviation < 0:
            raise AssertionError("DAO deviation underflow in reference model")

    def register(self, cluster_id: str, operator_ids: Iterable[int], validator_count: int = 1) -> Cluster:
        if cluster_id in self.clusters or validator_count <= 0:
            raise ValueError("cluster must be new and have validators")
        cluster = Cluster(cluster_id, tuple(operator_ids), validator_count)
        self.clusters[cluster_id] = cluster
        self._apply_operator_count(cluster.operator_ids, validator_count)
        self.dao_validator_count += validator_count
        self.assert_invariants()
        return cluster

    def update_eb(self, cluster_id: str, new_vunits: int) -> None:
        cluster = self.clusters[cluster_id]
        if not cluster.active:
            raise ValueError("model only applies EB accounting updates to active clusters")
        baseline = cluster.baseline()
        if new_vunits < baseline:
            raise ValueError("the reviewed model constrains EB to at least the 32 ETH baseline")
        old_vunits = cluster.effective_vunits()
        delta = new_vunits - old_vunits
        if delta:
            self._apply_deviation(cluster.operator_ids, delta)
        cluster.eb_vunits = new_vunits
        self.assert_invariants()

    def liquidate(self, cluster_id: str) -> None:
        cluster = self.clusters[cluster_id]
        if not cluster.active:
            raise ValueError("cluster is already inactive")
        deviation = max(cluster.effective_vunits() - cluster.baseline(), 0)
        self._apply_operator_count(cluster.operator_ids, -cluster.validator_count)
        self.dao_validator_count -= cluster.validator_count
        if deviation:
            self._apply_deviation(cluster.operator_ids, -deviation)
        cluster.active = False
        cluster.balance = 0
        # Retain eb_vunits: the source's reactivate path reuses the snapshot.
        self.assert_invariants()

    def reactivate(self, cluster_id: str, deposit: int = 1) -> None:
        cluster = self.clusters[cluster_id]
        if cluster.active:
            raise ValueError("cluster is already active")
        deviation = max(cluster.effective_vunits() - cluster.baseline(), 0)
        self._apply_operator_count(cluster.operator_ids, cluster.validator_count)
        self.dao_validator_count += cluster.validator_count
        if deviation:
            self._apply_deviation(cluster.operator_ids, deviation)
        cluster.active = True
        cluster.balance += deposit
        self.assert_invariants()

    def remove_validators(self, cluster_id: str, removed: int) -> None:
        cluster = self.clusters[cluster_id]
        if removed <= 0 or removed > cluster.validator_count:
            raise ValueError("invalid removal count")
        was_active = cluster.active
        if was_active:
            self._apply_operator_count(cluster.operator_ids, -removed)
            self.dao_validator_count -= removed
        cluster.validator_count -= removed

        if cluster.eb_vunits > 0:
            cluster.eb_vunits -= removed * BPS_DENOMINATOR
            if cluster.validator_count == 0:
                residual = cluster.eb_vunits
                # Active empty clusters remove residual deviation here. If already
                # liquidated, liquidation already removed it from global accounting.
                if residual > 0 and was_active:
                    self._apply_deviation(cluster.operator_ids, -residual)
                cluster.eb_vunits = 0
        self.assert_invariants()

    def expected_dao_vunits(self) -> int:
        return sum(c.effective_vunits() for c in self.clusters.values() if c.active)

    def expected_operator_vunits(self, operator_id: int) -> int:
        return sum(
            c.effective_vunits()
            for c in self.clusters.values()
            if c.active and operator_id in c.operator_ids
        )

    def dao_vunits(self) -> int:
        return self.dao_validator_count * BPS_DENOMINATOR + self.dao_deviation

    def operator_vunits(self, operator_id: int) -> int:
        return (
            self.operator_validator_count.get(operator_id, 0) * BPS_DENOMINATOR
            + self.operator_deviation.get(operator_id, 0)
        )

    def assert_invariants(self) -> None:
        assert self.dao_validator_count == sum(
            c.validator_count for c in self.clusters.values() if c.active
        )
        assert self.dao_vunits() == self.expected_dao_vunits(), (
            "DAO vUnits diverged", self.dao_vunits(), self.expected_dao_vunits()
        )
        operator_ids = set(self.operator_validator_count) | set(self.operator_deviation)
        for cluster in self.clusters.values():
            operator_ids.update(cluster.operator_ids)
        for operator_id in operator_ids:
            expected_count = sum(
                c.validator_count for c in self.clusters.values()
                if c.active and operator_id in c.operator_ids
            )
            assert self.operator_validator_count.get(operator_id, 0) == expected_count
            assert self.operator_vunits(operator_id) == self.expected_operator_vunits(operator_id), (
                "operator vUnits diverged", operator_id,
                self.operator_vunits(operator_id), self.expected_operator_vunits(operator_id)
            )


class StakingModel:
    """Reference model of the relevant cSSV hook/order, not a Solidity emulator."""

    def __init__(self, balances: dict[str, int], indexes: dict[str, int] | None = None) -> None:
        self.balances = dict(balances)
        self.total_supply = sum(balances.values())
        self.acc_per_share = 0
        self.user_index = dict(indexes or {})
        self.accrued: dict[str, int] = {user: 0 for user in balances}
        self.allowances: dict[tuple[str, str], int] = {}

    def sync_fees(self, new_fees: int) -> None:
        if new_fees < 0:
            raise ValueError("fees must not be negative")
        if self.total_supply:
            self.acc_per_share += (new_fees * PRECISION) // self.total_supply

    def settle(self, user: str) -> None:
        balance = self.balances.get(user, 0)
        previous_index = self.user_index.get(user, 0)
        if self.acc_per_share < previous_index:
            raise AssertionError("user index must not exceed global accumulator")
        self.accrued[user] = self.accrued.get(user, 0) + (
            balance * (self.acc_per_share - previous_index) // PRECISION
        )
        self.user_index[user] = self.acc_per_share

    def transfer(
        self, sender: str, recipient: str, amount: int, fees: int = 0,
        spender: str | None = None
    ) -> None:
        if amount < 0 or amount > self.balances.get(sender, 0):
            raise ValueError("invalid transfer amount")
        if spender is not None:
            key = (sender, spender)
            allowance = self.allowances.get(key, 0)
            if allowance < amount:
                raise ValueError("insufficient allowance")
            # OpenZeppelin transferFrom changes allowance before _transfer.
            self.allowances[key] = allowance - amount

        # CSSVToken._beforeTokenTransfer -> SSVStaking.onCSSVTransfer runs before
        # balances mutate; the hook settles the old token balances.
        if sender != recipient and amount > 0:
            self.sync_fees(fees)
            self.settle(sender)
            self.settle(recipient)
            self.balances[sender] -= amount
            self.balances[recipient] = self.balances.get(recipient, 0) + amount

    def request_unstake(self, user: str, amount: int, fees: int = 0) -> None:
        if amount <= 0 or amount > self.balances.get(user, 0):
            raise ValueError("invalid unstake amount")
        # The target calls _syncFees and settles with the pre-burn cSSV balance.
        self.sync_fees(fees)
        self.settle(user)
        self.balances[user] -= amount
        self.total_supply -= amount  # _burn bypasses the transfer hook for zero address

    def claimable_payout(self, user: str) -> int:
        amount = self.accrued.get(user, 0)
        return amount - (amount % ETH_DEDUCTED_DIGITS)
