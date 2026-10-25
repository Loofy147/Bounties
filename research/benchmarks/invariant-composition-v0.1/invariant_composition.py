"""Synthetic invariant checks; this module never connects to a chain.

Rules must be derived from a target's own specification before real use.
"""
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class AuditRecord:
    """Same-asset example: fee is actual fee, not just a user-supplied cap."""
    quantity: int
    fee: int
    source_debit: int
    payout_record: int


def check_transition_closure(
    *, collateral_before: int, debt_before: int,
    collateral_after: int, debt_after: int,
    requires_healthy_post_state: bool,
) -> List[str]:
    """Check only where the specification requires a healthy post-state."""
    findings: List[str] = []
    if requires_healthy_post_state and collateral_after < debt_after:
        findings.append("POST_STATE_INSOLVENT")
    return findings


def check_instruction_provenance(
    *, supplied_account_key: str, canonical_account_key: str,
    observed_program_id: str, expected_program_id: str,
) -> List[str]:
    """Check source-account identity and loaded program ID as separate guards."""
    findings: List[str] = []
    if supplied_account_key != canonical_account_key:
        findings.append("UNTRUSTED_INSTRUCTION_SOURCE")
    if observed_program_id != expected_program_id:
        findings.append("UNEXPECTED_INSTRUCTION_PROGRAM")
    return findings


def check_withdrawal_accounting(
    record: AuditRecord, *, allow_zero_quantity: bool = False,
) -> List[str]:
    """Check a simplified same-asset model: debit = principal + actual fee.

    Separate fee assets, escrow/lock semantics, burns, decimals, and rounding
    require a different target-specific accounting model.
    """
    findings: List[str] = []
    if record.quantity < 0:
        findings.append("NEGATIVE_WITHDRAWAL_QUANTITY")
    elif record.quantity == 0 and not allow_zero_quantity:
        findings.append("NON_POSITIVE_WITHDRAWAL")
    if record.fee < 0:
        findings.append("NEGATIVE_FEE")
    if record.source_debit != record.quantity + record.fee:
        findings.append("DEBIT_FORMULA_MISMATCH")
    if record.payout_record != record.quantity:
        findings.append("PAYOUT_RECORD_MISMATCH")
    if record.payout_record > 0 and record.source_debit < record.payout_record:
        findings.append("DEBIT_PAYOUT_MISMATCH")
    if record.source_debit < 0:
        findings.append("NEGATIVE_SOURCE_DEBIT")
    return findings
