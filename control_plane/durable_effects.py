"""Local durable effect journal reference model.

This module is intentionally local-only. It models a crash-recoverable
append-only journal for effect lifecycle state. It does not perform network
I/O or external side effects.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
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

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._records: list[JournalRecord] = []
        self._state: Dict[str, JournalRecord] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                raw = json.loads(line)
                record = JournalRecord(
                    sequence=int(raw["sequence"]),
                    effect_key=raw["effect_key"],
                    state=JournalEffectState(raw["state"]),
                    lease_id=raw["lease_id"],
                )
                current = self._state.get(record.effect_key)
                if current is not None and current.state != record.state:
                    self._validate_transition(current.state, record.state)
                self._records.append(record)
                self._state[record.effect_key] = record

    @staticmethod
    def _validate_transition(old: JournalEffectState, new: JournalEffectState) -> None:
        if new not in _ALLOWED[old]:
            raise ValueError(f"invalid effect transition: {old} -> {new}")

    def append(self, effect_key: str, lease_id: str, state: JournalEffectState) -> JournalRecord:
        with self._lock:
            current = self._state.get(effect_key)
            if current is not None:
                self._validate_transition(current.state, state)
            sequence = self._records[-1].sequence + 1 if self._records else 1
            record = JournalRecord(sequence, effect_key, state, lease_id)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")
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

    def verify_monotonic(self) -> bool:
        with self._lock:
            previous = 0
            for record in self._records:
                if record.sequence <= previous:
                    return False
                previous = record.sequence
            return True
