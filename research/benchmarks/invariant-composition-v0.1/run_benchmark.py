"""Deterministic seeded-defect benchmark. All scenarios are synthetic."""
import json
from typing import Any, Callable, Dict, List, Sequence

from invariant_composition import (
    AuditRecord,
    check_instruction_provenance,
    check_transition_closure,
    check_withdrawal_accounting,
)

Check = Callable[[], List[str]]


def _case(name: str, category: str, check: Check, expected: Sequence[str]) -> Dict[str, Any]:
    observed = sorted(check())
    expected_sorted = sorted(expected)
    passed = observed == expected_sorted if category == "seeded_defect" else observed == []
    return {
        "name": name,
        "category": category,
        "expected_findings": expected_sorted,
        "observed_findings": observed,
        "passed": passed,
    }


def run_benchmark() -> Dict[str, Any]:
    cases = [
        _case(
            "euler_like_missing_postcondition", "seeded_defect",
            lambda: check_transition_closure(
                collateral_before=200, debt_before=180,
                collateral_after=150, debt_after=180,
                requires_healthy_post_state=True,
            ),
            ["POST_STATE_INSOLVENT"],
        ),
        _case(
            "wormhole_like_untrusted_source_account", "seeded_defect",
            lambda: check_instruction_provenance(
                supplied_account_key="attacker-controlled-account",
                canonical_account_key="canonical-instructions-sysvar",
                observed_program_id="secp256k1-program",
                expected_program_id="secp256k1-program",
            ),
            ["UNTRUSTED_INSTRUCTION_SOURCE"],
        ),
        _case(
            "wax_like_negative_fee_and_unbacked_payout", "seeded_defect",
            lambda: check_withdrawal_accounting(
                AuditRecord(quantity=100, fee=-100, source_debit=0, payout_record=100)
            ),
            ["NEGATIVE_FEE", "DEBIT_PAYOUT_MISMATCH"],
        ),
        _case(
            "control_healthy_collateral_reduction", "negative_control",
            lambda: check_transition_closure(
                collateral_before=200, debt_before=180,
                collateral_after=190, debt_after=180,
                requires_healthy_post_state=True,
            ),
            [],
        ),
        _case(
            "control_canonical_sysvar_and_expected_program", "negative_control",
            lambda: check_instruction_provenance(
                supplied_account_key="canonical-instructions-sysvar",
                canonical_account_key="canonical-instructions-sysvar",
                observed_program_id="secp256k1-program",
                expected_program_id="secp256k1-program",
            ),
            [],
        ),
        _case(
            "control_valid_same_asset_withdrawal", "negative_control",
            lambda: check_withdrawal_accounting(
                AuditRecord(quantity=100, fee=5, source_debit=105, payout_record=100)
            ),
            [],
        ),
    ]
    seeded = [case for case in cases if case["category"] == "seeded_defect"]
    controls = [case for case in cases if case["category"] == "negative_control"]
    detected = sum(case["passed"] for case in seeded)
    passed_controls = sum(case["passed"] for case in controls)
    return {
        "benchmark": "invariant-composition-v0.1",
        "classification": "synthetic_model_only",
        "seeded_defects": {"detected": detected, "total": len(seeded)},
        "negative_controls": {"passed": passed_controls, "total": len(controls)},
        "cases": cases,
        "passed": detected == len(seeded) and passed_controls == len(controls),
        "limitations": [
            "Does not execute EVM, Solana, MoveVM, or bridge code.",
            "Rules must be derived from the actual target specification.",
            "A model pass proves neither vulnerability nor security of a real target.",
        ],
    }


def main() -> int:
    result = run_benchmark()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
