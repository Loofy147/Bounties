"""Local durable effect journal reference model.

This module is intentionally local-only. It models a crash-recoverable,
hash-linked append-only journal for effect lifecycle state. It does not
perform network I/O or external side effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
from threading import Lock
from typing import Dict


class JournalEffectState(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    PREPARED = "PREPARED"
    COMMITTED = "COMMITTED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    CANCELLED = "CANCELLED"
    REVOKED = "REVOKED"


@dataclass(frozen=True)
class JournalRecord:
    sequence: int
    effect_key: str
    state: JournalEffectState
    lease_id: str
    previous_hash: str
    record_hash: str


_ALLOWED = {
    JournalEffectState.AUTHORIZED: {JournalEffectState.PREPARED, JournalEffectState.CANCELLED, JournalEffectState.REVOKED},
    JournalEffectState.PREPARED: {JournalEffectState.COMMITTED, JournalEffectState.FAILED, JournalEffectState.UNKNOWN, JournalEffectState.CANCELLED, JournalEffectState.REVOKED},
    JournalEffectState.UNKNOWN: {JournalEffectState.COMMITTED, JournalEffectState.FAILED, JournalEffectState.REVOKED},
    JournalEffectState.COMMITTED: set(),
    JournalEffectState.FAILED: set(),
    JournalEffectState.CANCELLED: set(),
    JournalEffectState.REVOKED: set(),
}


class DurableEffectJournal:
    """Single-file append-only JSONL journal for local recovery tests."""

    GENESIS = "GENESIS"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._records: list[JournalRecord] = []
        self._state: Dict[str, JournalRecord] = {}
        self._load()

    @staticmethod
    def _canonical(sequence: int, effect_key: str, state: JournalEffectState,
                   lease_id: str, previous_hash: str) -> str:
        return "|".join((
            str(sequence), effect_key, state.value, lease_id, previous_hash
        ))

    @classmethod
    def _hash_record(cls, sequence: int, effect_key: str,
                     state: JournalEffectState, lease_id: str,
                     previous_hash: str) -> str:
        return sha256(
            cls._canonical(sequence, effect_key, state, lease_id, previous_hash).encode("utf-8")
        ).hexdigest()

    def _load(self) -> None:
        if not self.path.exists():
            return
        previous_hash = self.GENESIS
        previous_sequence = 0
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                raw = json.loads(line)
                sequence = int(raw["sequence"])
                effect_key = raw["effect_key"]
                state = JournalEffectState(raw["state"])
                lease_id = raw["lease_id"]
                expected_hash = self._hash_record(
                    sequence, effect_key, state, lease_id, previous_hash
                )
                if sequence != previous_sequence + 1:
                    raise ValueError("non-monotonic journal sequence")
                if raw["previous_hash"] != previous_hash:
                    raise ValueError("broken journal hash chain")
                if raw["record_hash"] != expected_hash:
                    raise ValueError("journal integrity check failed")
                current = self._state.get(effect_key)
                if current is not None:
                    if current.lease_id != lease_id:
                        raise ValueError("effect identity rebound to another lease")
                    self._validate_transition(current.state, state)
                record = JournalRecord(
                    sequence=sequence,
                    effect_key=effect_key,
                    state=state,
                    lease_id=lease_id,
                    previous_hash=previous_hash,
                    record_hash=expected_hash,
                )
                self._records.append(record)
                self._state[effect_key] = record
                previous_hash = expected_hash
                previous_sequence = sequence

    @staticmethod
    def _validate_transition(old: JournalEffectState, new: JournalEffectState) -> None:
        if new not in _ALLOWED[old]:
            raise ValueError(f"invalid effect transition: {old} -> {new}")

    def append(self, effect_key: str, lease_id: str, state: JournalEffectState) -> JournalRecord:
        with self._lock:
            current = self._state.get(effect_key)
            if current is not None:
                if current.lease_id != lease_id:
                    raise ValueError("effect identity rebound to another lease")
                self._validate_transition(current.state, state)
            sequence = self._records[-1].sequence + 1 if self._records else 1
            previous_hash = self._records[-1].record_hash if self._records else self.GENESIS
            record_hash = self._hash_record(
                sequence, effect_key, state, lease_id, previous_hash
            )
            record = JournalRecord(
                sequence, effect_key, state, lease_id, previous_hash, record_hash
            )
            raw = {
                "sequence": sequence,
                "effect_key": effect_key,
                "state": state.value,
                "lease_id": lease_id,
                "previous_hash": previous_hash,
                "record_hash": record_hash,
            }
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(raw, sort_keys=True) + "\n")
                handle.flush()
            self._records.append(record)
            self._state[effect_key] = record
            return record

    def get(self, effect_key: str) -> JournalRecord:
        with self._lock:
            try:
                return self._state[effect_key]
            except KeyError as exc:
                raise KeyError(effect_key) from exc

    def unresolved(self) -> tuple[JournalRecord, ...]:
        with self._lock:
            return tuple(
                record for record in self._state.values()
                if record.state in {JournalEffectState.PREPARED, JournalEffectState.UNKNOWN}
            )

    def verify_integrity(self) -> bool:
        with self._lock:
            previous_hash = self.GENESIS
            previous_sequence = 0
            for record in self._records:
                if record.sequence != previous_sequence + 1:
                    return False
                if record.previous_hash != previous_hash:
                    return False
                expected = self._hash_record(
                    record.sequence,
                    record.effect_key,
                    record.state,
                    record.lease_id,
                    previous_hash,
                )
                if record.record_hash != expected:
                    return False
                previous_hash = expected
                previous_sequence = record.sequence
            return True
