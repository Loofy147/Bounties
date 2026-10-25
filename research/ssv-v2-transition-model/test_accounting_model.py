import unittest

from accounting_model import BPS_DENOMINATOR, EBAccountingModel, StakingModel


class EBTransitionLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.model = EBAccountingModel()

    def test_liquidate_reactivate_round_trip_restores_snapshot_deviation(self):
        cluster = self.model.register("A", [1, 2], 1)
        self.model.update_eb("A", 640_000)  # 2048 ETH effective balance, one validator
        before = (
            self.model.dao_vunits(),
            self.model.operator_vunits(1),
            self.model.operator_vunits(2),
        )
        self.model.liquidate("A")
        self.assertEqual(self.model.dao_vunits(), 0)
        self.assertEqual(cluster.eb_vunits, 640_000)
        self.model.reactivate("A", deposit=10)
        self.assertEqual(
            (self.model.dao_vunits(), self.model.operator_vunits(1), self.model.operator_vunits(2)),
            before,
        )

    def test_remove_last_validator_after_liquidation_does_not_double_subtract_deviation(self):
        self.model.register("A", [1, 2], 1)
        self.model.update_eb("A", 640_000)
        self.model.liquidate("A")
        self.model.remove_validators("A", 1)
        self.assertEqual(self.model.dao_vunits(), 0)
        self.assertEqual(self.model.operator_vunits(1), 0)
        self.assertEqual(self.model.operator_vunits(2), 0)
        self.assertEqual(self.model.clusters["A"].eb_vunits, 0)

    def test_reactivate_then_remove_last_validator_cleans_restored_deviation_once(self):
        self.model.register("A", [1, 2], 1)
        self.model.update_eb("A", 640_000)
        self.model.liquidate("A")
        self.model.reactivate("A")
        self.model.remove_validators("A", 1)
        self.assertEqual(self.model.dao_vunits(), 0)
        self.assertEqual(self.model.operator_vunits(1), 0)
        self.assertEqual(self.model.operator_vunits(2), 0)
        self.assertEqual(self.model.clusters["A"].eb_vunits, 0)

    def test_shared_operator_other_cluster_is_unchanged_by_one_cluster_cycle(self):
        self.model.register("A", [1, 9], 1)
        self.model.update_eb("A", 640_000)
        self.model.register("B", [1, 8], 1)
        before_b = self.model.clusters["B"].effective_vunits()
        before_total = self.model.operator_vunits(1)
        self.model.liquidate("A")
        self.model.reactivate("A")
        self.assertEqual(self.model.clusters["B"].effective_vunits(), before_b)
        self.assertEqual(self.model.operator_vunits(1), before_total)

    def test_eb_decrease_after_reactivation_then_remove_preserves_accounting(self):
        self.model.register("A", [1, 2], 1)
        self.model.update_eb("A", 640_000)
        self.model.liquidate("A")
        self.model.reactivate("A")
        self.model.update_eb("A", BPS_DENOMINATOR)
        self.assertEqual(self.model.dao_vunits(), BPS_DENOMINATOR)
        self.model.remove_validators("A", 1)
        self.assertEqual(self.model.dao_vunits(), 0)
        self.assertEqual(self.model.operator_vunits(1), 0)

    def test_multiple_lifecycle_cycles_are_idempotent_in_aggregate(self):
        self.model.register("A", [1, 2, 3, 4], 2)
        self.model.update_eb("A", 1_280_000)
        expected = self.model.dao_vunits()
        for _ in range(5):
            self.model.liquidate("A")
            self.assertEqual(self.model.dao_vunits(), 0)
            self.model.reactivate("A")
            self.assertEqual(self.model.dao_vunits(), expected)
            self.model.assert_invariants()


class CSSVTransferOrderTests(unittest.TestCase):
    def test_transfer_from_settles_pretransfer_balance_not_posttransfer_balance(self):
        model = StakingModel({"owner": 100, "receiver": 20})
        model.user_index = {"owner": 0, "receiver": 0}
        model.allowances[("owner", "spender")] = 40
        model.transfer("owner", "receiver", 40, fees=120, spender="spender")
        self.assertEqual(model.accrued["owner"], 100)
        self.assertEqual(model.accrued["receiver"], 20)
        self.assertEqual(model.balances, {"owner": 60, "receiver": 60})
        self.assertEqual(model.allowances[("owner", "spender")], 0)

    def test_transfer_then_immediate_unstake_does_not_double_credit_received_shares(self):
        model = StakingModel({"A": 100, "B": 20})
        model.user_index = {"A": 0, "B": 0}
        model.transfer("A", "B", 40, fees=120)
        self.assertEqual(model.accrued["A"], 100)
        self.assertEqual(model.accrued["B"], 20)
        model.request_unstake("B", 60, fees=0)
        self.assertEqual(model.accrued["B"], 20)
        self.assertEqual(model.balances["B"], 0)
        self.assertEqual(model.total_supply, 60)

    def test_same_accumulator_multi_hop_does_not_erase_or_duplicate_first_period_rewards(self):
        model = StakingModel({"A": 100, "B": 20, "C": 30})
        model.user_index = {"A": 0, "B": 0, "C": 0}
        model.transfer("A", "B", 40, fees=150)
        model.transfer("B", "C", 25, fees=0)
        self.assertEqual(model.accrued, {"A": 100, "B": 20, "C": 30})
        self.assertEqual(sum(model.accrued.values()), 150)
        self.assertEqual(model.balances, {"A": 60, "B": 35, "C": 55})

    def test_later_unstake_settles_current_holder_balance_for_new_fee_window(self):
        model = StakingModel({"A": 100, "B": 20, "C": 30})
        model.user_index = {"A": 0, "B": 0, "C": 0}
        model.transfer("A", "B", 40, fees=150)
        model.transfer("B", "C", 25, fees=0)
        model.request_unstake("B", 10, fees=120)
        self.assertEqual(model.accrued["B"], 48)  # 20 old-period + floor(35 * 0.8)
        self.assertEqual(model.balances["B"], 25)

    def test_one_wei_remaining_keeps_dust_claimable_balance_for_future_accrual(self):
        model = StakingModel({"owner": 100_001})
        model.user_index = {"owner": 0}
        model.accrued["owner"] = 99_999
        model.transfer("owner", "receiver", 100_000, fees=0)
        self.assertEqual(model.balances["owner"], 1)
        self.assertEqual(model.claimable_payout("owner"), 0)
        model.accrued["owner"] += 1
        self.assertEqual(model.claimable_payout("owner"), 100_000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
