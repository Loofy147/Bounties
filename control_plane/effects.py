"""Local-only side-effect state protocol.

This module models the authorization-to-effect boundary without performing
network I/O or real external side effects. It explicitly represents UNKNOWN
outcomes so a worker crash cannot silently become permission to retry an
unknown external effect.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from threading import Lock
from typing import Optional

from .kernel import ControlPlane, Lease


class EffectState(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    PREPARED = "PREPARED"
    COMMITTED = "COMMITTED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    CANCELLED = "CANCELLED"
    REVOKED = "REVOKED"


@dataclass(frozen=True)
class EffectRecord:
    effect_key: str
    lease_id: str
    state: EffectState
    attempt: int = 0
    result_digest: Optional[str] = None


class EffectLedger:
    """Thread-safe local reference ledger for durable-effect semantics."""

    def __init__(self) -> None:
        self._records: dict[str, EffectRecord] = {}
        self._lock = Lock()

    def register(self, lease: Lease) -> EffectRecord:
        with self._lock:
            existing = self._records.get(lease.effect_key)
            if existing is not None:
                raise PermissionError("duplicate effect identity")
            record = EffectRecord(
                effect_key=lease.effect_key,
                lease_id=lease.lease_id,
                state=EffectState.AUTHORIZED,
            )
            self._records[lease.effect_key] = record
            return record

    def transition(self, effect_key: str, expected: EffectState,
                   new_state: EffectState, result_digest: Optional[str] = None) -> EffectRecord:
        with self._lock:
            record = self._records.get(effect_key)
            if record is None:
                raise KeyError(effect_key)
            if record.state != expected:
                raise PermissionError(f"invalid effect transition from {record.state}")
            updated = replace(
                record,
                state=new_state,
                result_digest=result_digest,
                attempt=record.attempt + (1 if new_state == EffectState.PREPARED else 0),
            )
            self._records[effect_key] = updated
            return updated

    def get(self, effect_key: str) -> EffectRecord:
        with self._lock:
            record = self._records.get(effect_key)
            if record is None:
                raise KeyError(effect_key)
            return record


class LocalEffectProtocol:
    """Models prepare/commit/unknown semantics without real side effects."""

    def __init__(self, control_plane: ControlPlane, ledger: EffectLedger) -> None:
        self.control_plane = control_plane
        self.ledger = ledger

    def authorize_effect(self, lease: Lease) -> EffectRecord:
        return self.ledger.register(lease)

    def prepare(self, effect_key: str) -> EffectRecord:
        return self.ledger.transition(
            effect_key, EffectState.AUTHORIZED, EffectState.PREPARED
        )

    def mark_committed(self, effect_key: str, result_digest: str) -> EffectRecord:
        return self.ledger.transition(
            effect_key, EffectState.PREPARED, EffectState.COMMITTED, result_digest
        )

    def mark_failed(self, effect_key: str, result_digest: Optional[str] = None) -> EffectRecord:
        return self.ledger.transition(
            effect_key, EffectState.PREPARED, EffectState.FAILED, result_digest
        )

    def mark_unknown(self, effect_key: str) -> EffectRecord:
        return self.ledger.transition(
            effect_key, EffectState.PREPARED, EffectState.UNKNOWN
        )

    def recover_unknown(self, effect_key: str) -> EffectRecord:
        """Unknown effects cannot be retried by inference.

        A concrete executor must reconcile external state using its durable
        effect identity before any retry can be considered.
        """
        record = self.ledger.get(effect_key)
        if record.state != EffectState.UNKNOWN:
            raise PermissionError("effect is not unknown")
        raise RuntimeError("external reconciliation required before retry")
