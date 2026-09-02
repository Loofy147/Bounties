"""Local-only single-owner authority for effect execution.

This module proves the next Control Plane gate: one stable effect identity may
have at most one active execution owner. Ownership uses monotonically
increasing fencing tokens so a stale worker cannot remain valid after a new
owner is admitted.

No network I/O, external side effects, or distributed consensus are provided.
The implementation is a deterministic reference model for the later durable
multi-worker authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from threading import Lock
from typing import Callable, Optional


class OwnershipState(str, Enum):
    UNOWNED = "UNOWNED"
    OWNED = "OWNED"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


@dataclass(frozen=True)
class OwnershipRecord:
    effect_key: str
    state: OwnershipState
    owner_id: Optional[str]
    fencing_token: int
    version: int
    acquired_at: Optional[datetime]
    expires_at: Optional[datetime]


class OwnershipConflict(PermissionError):
    """Raised when a requested ownership operation is not admissible."""


class StaleOwner(OwnershipConflict):
    """Raised when a caller presents an old fencing token or owner identity."""


class OwnershipAuthority:
    """Thread-safe local CAS-style authority for effect ownership."""

    def __init__(
        self,
        now: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self._records: dict[str, OwnershipRecord] = {}
        self._tokens: dict[str, int] = {}
        self._lock = Lock()
        self._now = now or (lambda: datetime.now(timezone.utc))

    def _validate_ttl(self, ttl: timedelta) -> None:
        if ttl <= timedelta(0):
            raise ValueError("ttl must be positive")

    def _expire_if_needed(self, effect_key: str, now: datetime) -> OwnershipRecord | None:
        record = self._records.get(effect_key)
        if record is None:
            return None
        if record.state == OwnershipState.OWNED and record.expires_at is not None:
            if record.expires_at <= now:
                expired = OwnershipRecord(
                    effect_key=record.effect_key,
                    state=OwnershipState.EXPIRED,
                    owner_id=None,
                    fencing_token=record.fencing_token,
                    version=record.version + 1,
                    acquired_at=record.acquired_at,
                    expires_at=record.expires_at,
                )
                self._records[effect_key] = expired
                return expired
        return record

    def claim(self, effect_key: str, owner_id: str, ttl: timedelta) -> OwnershipRecord:
        if not effect_key:
            raise ValueError("effect_key must be non-empty")
        if not owner_id:
            raise ValueError("owner_id must be non-empty")
        self._validate_ttl(ttl)

        now = self._now()
        with self._lock:
            current = self._expire_if_needed(effect_key, now)
            if current is not None and current.state == OwnershipState.OWNED:
                raise OwnershipConflict("effect already has an active owner")
            if current is not None and current.state == OwnershipState.REVOKED:
                raise OwnershipConflict("effect ownership is revoked")

            token = self._tokens.get(effect_key, 0) + 1
            self._tokens[effect_key] = token
            record = OwnershipRecord(
                effect_key=effect_key,
                state=OwnershipState.OWNED,
                owner_id=owner_id,
                fencing_token=token,
                version=(current.version + 1) if current else 1,
                acquired_at=now,
                expires_at=now + ttl,
            )
            self._records[effect_key] = record
            return record

    def renew(
        self,
        effect_key: str,
        owner_id: str,
        fencing_token: int,
        ttl: timedelta,
    ) -> OwnershipRecord:
        self._validate_ttl(ttl)
        now = self._now()
        with self._lock:
            current = self._expire_if_needed(effect_key, now)
            self._require_current_owner(current, owner_id, fencing_token)
            renewed = OwnershipRecord(
                effect_key=current.effect_key,
                state=OwnershipState.OWNED,
                owner_id=current.owner_id,
                fencing_token=current.fencing_token,
                version=current.version + 1,
                acquired_at=current.acquired_at,
                expires_at=now + ttl,
            )
            self._records[effect_key] = renewed
            return renewed

    def release(self, effect_key: str, owner_id: str, fencing_token: int) -> OwnershipRecord:
        now = self._now()
        with self._lock:
            current = self._expire_if_needed(effect_key, now)
            self._require_current_owner(current, owner_id, fencing_token)
            released = OwnershipRecord(
                effect_key=current.effect_key,
                state=OwnershipState.RELEASED,
                owner_id=None,
                fencing_token=current.fencing_token,
                version=current.version + 1,
                acquired_at=current.acquired_at,
                expires_at=None,
            )
            self._records[effect_key] = released
            return released

    def revoke(self, effect_key: str) -> OwnershipRecord:
        now = self._now()
        with self._lock:
            current = self._expire_if_needed(effect_key, now)
            if current is None:
                current = OwnershipRecord(
                    effect_key=effect_key,
                    state=OwnershipState.UNOWNED,
                    owner_id=None,
                    fencing_token=self._tokens.get(effect_key, 0),
                    version=0,
                    acquired_at=None,
                    expires_at=None,
                )
            revoked = OwnershipRecord(
                effect_key=effect_key,
                state=OwnershipState.REVOKED,
                owner_id=None,
                fencing_token=current.fencing_token,
                version=current.version + 1,
                acquired_at=current.acquired_at,
                expires_at=current.expires_at if current.state == OwnershipState.OWNED else None,
            )
            self._records[effect_key] = revoked
            return revoked

    def current(self, effect_key: str) -> OwnershipRecord:
        now = self._now()
        with self._lock:
            current = self._expire_if_needed(effect_key, now)
            if current is None:
                raise KeyError(effect_key)
            return current

    def assert_current(self, effect_key: str, owner_id: str, fencing_token: int) -> OwnershipRecord:
        now = self._now()
        with self._lock:
            current = self._expire_if_needed(effect_key, now)
            self._require_current_owner(current, owner_id, fencing_token)
            return current

    @staticmethod
    def _require_current_owner(
        record: OwnershipRecord | None,
        owner_id: str,
        fencing_token: int,
    ) -> None:
        if record is None:
            raise StaleOwner("effect has no owner")
        if record.state != OwnershipState.OWNED:
            raise StaleOwner(f"effect is not owned: {record.state}")
        if record.owner_id != owner_id or record.fencing_token != fencing_token:
            raise StaleOwner("stale owner or fencing token")
