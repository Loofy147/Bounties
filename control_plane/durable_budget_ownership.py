"""Transactional local ownership + budget reservation authority.

This module is a local reference implementation for the invariant that effect
ownership and its pessimistic budget reservation are admitted together in one
SQLite transaction. It performs no network I/O or external side effects.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional


class AtomicAdmissionConflict(PermissionError):
    """Raised when ownership or budget admission cannot be granted."""


class AtomicStaleOwner(AtomicAdmissionConflict):
    """Raised when the presented owner/fencing token is no longer current."""


@dataclass(frozen=True)
class AtomicOwnershipRecord:
    effect_key: str
    budget_key: str
    owner_id: Optional[str]
    fencing_token: int
    version: int
    reservation: Decimal
    state: str
    expires_at: Optional[str]


class SQLiteAtomicAuthority:
    """Shared local authority for ownership and pessimistic budget admission."""

    def __init__(self, path: str | Path, budget_key: str, ceiling: Decimal) -> None:
        if not budget_key:
            raise ValueError("budget_key must be non-empty")
        if ceiling < 0:
            raise ValueError("budget ceiling must be non-negative")
        self.path = str(path)
        self.budget_key = budget_key
        self._initialize(ceiling)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10.0, isolation_level=None)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=10000")
        return conn

    def _initialize(self, ceiling: Decimal) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS budget_state (
                    budget_key TEXT PRIMARY KEY,
                    ceiling TEXT NOT NULL,
                    reserved TEXT NOT NULL,
                    consumed TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS atomic_ownership (
                    effect_key TEXT PRIMARY KEY,
                    budget_key TEXT NOT NULL,
                    owner_id TEXT,
                    fencing_token INTEGER NOT NULL,
                    version INTEGER NOT NULL,
                    reservation TEXT NOT NULL,
                    state TEXT NOT NULL,
                    expires_at TEXT
                )
                """
            )
            existing = conn.execute(
                "SELECT 1 FROM budget_state WHERE budget_key=?", (self.budget_key,)
            ).fetchone()
            if existing is None:
                conn.execute(
                    "INSERT INTO budget_state VALUES (?,?,?,?)",
                    (self.budget_key, str(ceiling), "0", "0"),
                )

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _parse_decimal(value: str) -> Decimal:
        try:
            return Decimal(value)
        except InvalidOperation as exc:
            raise ValueError("corrupt decimal in authority") from exc

    @staticmethod
    def _parse_time(value: Optional[str]) -> Optional[datetime]:
        return datetime.fromisoformat(value) if value else None

    @classmethod
    def _record(cls, row: tuple) -> AtomicOwnershipRecord:
        return AtomicOwnershipRecord(
            effect_key=row[0],
            budget_key=row[1],
            owner_id=row[2],
            fencing_token=int(row[3]),
            version=int(row[4]),
            reservation=cls._parse_decimal(row[5]),
            state=row[6],
            expires_at=row[7],
        )

    @staticmethod
    def _validate_inputs(effect_key: str, owner_id: str, reservation: Decimal, ttl: timedelta) -> None:
        if not effect_key:
            raise ValueError("effect_key must be non-empty")
        if not owner_id:
            raise ValueError("owner_id must be non-empty")
        if reservation < 0:
            raise ValueError("reservation must be non-negative")
        if ttl <= timedelta(0):
            raise ValueError("ttl must be positive")

    def claim(
        self,
        effect_key: str,
        owner_id: str,
        reservation: Decimal,
        ttl: timedelta,
    ) -> AtomicOwnershipRecord:
        """Atomically claim ownership and reserve budget for one effect."""
        self._validate_inputs(effect_key, owner_id, reservation, ttl)
        now = self._now()
        expires_at = (now + ttl).isoformat()

        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            budget = conn.execute(
                "SELECT ceiling,reserved,consumed FROM budget_state WHERE budget_key=?",
                (self.budget_key,),
            ).fetchone()
            assert budget is not None
            ceiling = self._parse_decimal(budget[0])
            reserved = self._parse_decimal(budget[1])
            consumed = self._parse_decimal(budget[2])

            row = conn.execute(
                "SELECT effect_key,budget_key,owner_id,fencing_token,version,reservation,state,expires_at "
                "FROM atomic_ownership WHERE effect_key=?",
                (effect_key,),
            ).fetchone()

            if row is not None:
                current = self._record(row)
                expires = self._parse_time(current.expires_at)
                if current.state == "REVOKED":
                    raise AtomicAdmissionConflict("effect ownership is revoked")
                if current.state == "OWNED" and expires is not None and expires > now:
                    raise AtomicAdmissionConflict("effect already has an active owner")

                # Expired ownership loses execution authority, but its reservation
                # is explicitly released inside the same transaction that grants
                # the replacement owner.
                if current.state == "OWNED":
                    reserved -= current.reservation
                    conn.execute(
                        "UPDATE atomic_ownership SET state='EXPIRED', owner_id=NULL, reservation='0', version=version+1 "
                        "WHERE effect_key=? AND state='OWNED'",
                        (effect_key,),
                    )
                    version = current.version + 1
                else:
                    version = current.version
                fencing_token = current.fencing_token + 1
                next_version = version + 1
                if reservation > ceiling - reserved - consumed:
                    raise AtomicAdmissionConflict("budget reservation denied")
                conn.execute(
                    """
                    UPDATE atomic_ownership
                    SET budget_key=?, owner_id=?, fencing_token=?, version=?,
                        reservation=?, state='OWNED', expires_at=?
                    WHERE effect_key=?
                    """,
                    (
                        self.budget_key,
                        owner_id,
                        fencing_token,
                        next_version,
                        str(reservation),
                        expires_at,
                        effect_key,
                    ),
                )
            else:
                fencing_token = 1
                next_version = 1
                if reservation > ceiling - reserved - consumed:
                    raise AtomicAdmissionConflict("budget reservation denied")
                conn.execute(
                    """
                    INSERT INTO atomic_ownership
                    (effect_key,budget_key,owner_id,fencing_token,version,reservation,state,expires_at)
                    VALUES (?,?,?,?,?,?,?,?)
                    """,
                    (
                        effect_key,
                        self.budget_key,
                        owner_id,
                        fencing_token,
                        next_version,
                        str(reservation),
                        "OWNED",
                        expires_at,
                    ),
                )

            new_reserved = reserved + reservation
            conn.execute(
                "UPDATE budget_state SET reserved=? WHERE budget_key=?",
                (str(new_reserved), self.budget_key),
            )
            conn.commit()
            row = conn.execute(
                "SELECT effect_key,budget_key,owner_id,fencing_token,version,reservation,state,expires_at "
                "FROM atomic_ownership WHERE effect_key=?",
                (effect_key,),
            ).fetchone()
            assert row is not None
            return self._record(row)

    def assert_current(self, effect_key: str, owner_id: str, fencing_token: int) -> AtomicOwnershipRecord:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT effect_key,budget_key,owner_id,fencing_token,version,reservation,state,expires_at "
                "FROM atomic_ownership WHERE effect_key=?",
                (effect_key,),
            ).fetchone()
            if row is None:
                raise AtomicStaleOwner("effect has no ownership record")
            current = self._record(row)
            expires = self._parse_time(current.expires_at)
            if current.state != "OWNED":
                raise AtomicStaleOwner(f"effect is not owned: {current.state}")
            if expires is not None and expires <= self._now():
                raise AtomicStaleOwner("ownership has expired")
            if current.owner_id != owner_id or current.fencing_token != fencing_token:
                raise AtomicStaleOwner("stale owner or fencing token")
            return current

    def release(self, effect_key: str, owner_id: str, fencing_token: int) -> AtomicOwnershipRecord:
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT effect_key,budget_key,owner_id,fencing_token,version,reservation,state,expires_at "
                "FROM atomic_ownership WHERE effect_key=?",
                (effect_key,),
            ).fetchone()
            if row is None:
                raise AtomicStaleOwner("effect has no ownership record")
            current = self._record(row)
            self._require_current(current, owner_id, fencing_token)
            budget = conn.execute(
                "SELECT reserved FROM budget_state WHERE budget_key=?", (current.budget_key,)
            ).fetchone()
            assert budget is not None
            reserved = self._parse_decimal(budget[0])
            if current.reservation > reserved:
                raise ValueError("corrupt budget reservation")
            conn.execute(
                "UPDATE budget_state SET reserved=? WHERE budget_key=?",
                (str(reserved - current.reservation), current.budget_key),
            )
            conn.execute(
                "UPDATE atomic_ownership SET state='RELEASED', owner_id=NULL, reservation='0', expires_at=NULL, version=version+1 "
                "WHERE effect_key=? AND state='OWNED'",
                (effect_key,),
            )
            conn.commit()
            return self._record(conn.execute(
                "SELECT effect_key,budget_key,owner_id,fencing_token,version,reservation,state,expires_at "
                "FROM atomic_ownership WHERE effect_key=?", (effect_key,)
            ).fetchone())

    def budget(self) -> tuple[Decimal, Decimal, Decimal]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT ceiling,reserved,consumed FROM budget_state WHERE budget_key=?",
                (self.budget_key,),
            ).fetchone()
            assert row is not None
            return tuple(self._parse_decimal(v) for v in row)  # type: ignore[return-value]

    @staticmethod
    def _require_current(record: AtomicOwnershipRecord, owner_id: str, fencing_token: int) -> None:
        expires = SQLiteAtomicAuthority._parse_time(record.expires_at)
        if record.state != "OWNED":
            raise AtomicStaleOwner(f"effect is not owned: {record.state}")
        if expires is not None and expires <= SQLiteAtomicAuthority._now():
            raise AtomicStaleOwner("ownership has expired")
        if record.owner_id != owner_id or record.fencing_token != fencing_token:
            raise AtomicStaleOwner("stale owner or fencing token")
