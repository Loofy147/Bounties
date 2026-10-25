import unittest

from invariant_composition import (
    AuditRecord,
    check_instruction_provenance,
    check_transition_closure,
    check_withdrawal_accounting,
)
from run_benchmark import run_benchmark


class TransitionClosureTests(unittest.TestCase):
    def test_healthy_donation_control_passes(self):
        self.assertEqual(check_transition_closure(
            collateral_before=200, debt_before=180,
            collateral_after=190, debt_after=180,
            requires_healthy_post_state=True,
        ), [])

    def test_missing_health_guard_is_detected(self):
        self.assertIn("POST_STATE_INSOLVENT", check_transition_closure(
            collateral_before=200, debt_before=180,
            collateral_after=150, debt_after=180,
            requires_healthy_post_state=True,
        ))

    def test_unconstrained_transition_is_not_misclassified(self):
        self.assertEqual(check_transition_closure(
            collateral_before=100, debt_before=120,
            collateral_after=100, debt_after=120,
            requires_healthy_post_state=False,
        ), [])


class ProvenanceTests(unittest.TestCase):
    def test_canonical_source_and_expected_program_pass(self):
        self.assertEqual(check_instruction_provenance(
            supplied_account_key="canonical-instructions-sysvar",
            canonical_account_key="canonical-instructions-sysvar",
            observed_program_id="secp256k1-program",
            expected_program_id="secp256k1-program",
        ), [])

    def test_spoofed_source_is_detected_even_if_program_looks_valid(self):
        self.assertIn("UNTRUSTED_INSTRUCTION_SOURCE", check_instruction_provenance(
            supplied_account_key="attacker-controlled-account",
            canonical_account_key="canonical-instructions-sysvar",
            observed_program_id="secp256k1-program",
            expected_program_id="secp256k1-program",
        ))

    def test_wrong_instruction_program_is_detected(self):
        self.assertIn("UNEXPECTED_INSTRUCTION_PROGRAM", check_instruction_provenance(
            supplied_account_key="canonical-instructions-sysvar",
            canonical_account_key="canonical-instructions-sysvar",
            observed_program_id="attacker-program",
            expected_program_id="secp256k1-program",
        ))


class WithdrawalAccountingTests(unittest.TestCase):
    def test_valid_withdrawal_passes(self):
        self.assertEqual(check_withdrawal_accounting(
            AuditRecord(quantity=100, fee=5, source_debit=105, payout_record=100)
        ), [])

    def test_negative_fee_and_underbacked_payout_are_detected(self):
        findings = check_withdrawal_accounting(
            AuditRecord(quantity=100, fee=-100, source_debit=0, payout_record=100)
        )
        self.assertIn("NEGATIVE_FEE", findings)
        self.assertIn("DEBIT_PAYOUT_MISMATCH", findings)

    def test_zero_quantity_follows_explicit_policy(self):
        record = AuditRecord(quantity=0, fee=0, source_debit=0, payout_record=0)
        self.assertIn("NON_POSITIVE_WITHDRAWAL", check_withdrawal_accounting(record))
        self.assertEqual(check_withdrawal_accounting(record, allow_zero_quantity=True), [])

    def test_nonnegative_fee_does_not_hide_insufficient_debit(self):
        findings = check_withdrawal_accounting(
            AuditRecord(quantity=100, fee=5, source_debit=90, payout_record=100)
        )
        self.assertIn("DEBIT_PAYOUT_MISMATCH", findings)


class BenchmarkRunnerTests(unittest.TestCase):
    def test_all_seeded_defects_are_detected_and_controls_stay_clean(self):
        result = run_benchmark()
        self.assertEqual(result["seeded_defects"], {"detected": 3, "total": 3})
        self.assertEqual(result["negative_controls"], {"passed": 3, "total": 3})
        self.assertTrue(result["passed"])


if __name__ == "__main__":
    unittest.main()
