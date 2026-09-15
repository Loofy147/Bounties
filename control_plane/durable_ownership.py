"""Multi-process reference authority for effect ownership.

SQLite WAL is used here as a local durable concurrency boundary. The module
proves the ownership invariant across independent processes without performing
network I/O or external side effects.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


class DurableOwnershipState(str, Enum):
    UNOWNED = "UNOWNED"
    OWNED = "OWNED"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


@dataclass(frozen=True)
class DurableOwnershipRecord:
    effect_key: str
    state: DurableOwnershipState
    owner_id: Optional[str]
    fencing_token: int
    version: int
    acquired_at: Optional[str]
    expires_at: Optional[str]


class DurableOwnershipConflict(PermissionError):
    """Raised when the durable authority rejects an ownership operation."""


class DurableStaleOwner(DurableOwnershipConflict):
    """Raised when the presented owner or fencing token is stale."""


class SQLiteOwnershipAuthority:
    """Durable local multi-process ownership authority."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.path,
            timeout=10.0,
            isolation_level=None,
        )
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=10000")
        return conn

    def _initialize(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS effect_ownership (
                    effect_key TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    owner_id TEXT,
                    fencing_token INTEGER NOT NULL,
                    version INTEGER NOT NULL,
                    acquired_at TEXT,
                    expires_at TEXT
                )
                """
            )

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _parse_time(value: Optional[str]) -> Optional[datetime]:
        return datetime.fromisoformat(value) if value is not None else None

    @classmethod
    def _record(cls, row: tuple) -> DurableOwnershipRecord:
        return DurableOwnershipRecord(
            effect_key=row[0],
            state=DurableOwnershipState(row[1]),
            owner_id=row[2],
            fencing_token=int(row[3]),
            version=int(row[4]),
            acquired_at=row[5],
            expires_at=row[6],
        )

    @staticmethod
    def _validate_ttl(ttl: timedelta) -> None:
        if ttl <= timedelta(0):
            raise ValueError("ttl must be positive")

    def claim(self, effect_key: str, owner_id: str, ttl: timedelta) -> DurableOwnershipRecord:
        if not effect_key:
            raise ValueError("effect_key must be non-empty")
        if not owner_id:
            raise ValueError("owner_id must be non-empty")
        self._validate_ttl(ttl)

        now = self._now()
        now_s = now.isoformat()
        expires_s = (now + ttl).isoformat()
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT effect_key,state,owner_id,fencing_token,version,acquired_at,expires_at "
                "FROM effect_ownership WHERE effect_key=?",
                (effect_key,),
            ).fetchone()

            if row is not None:
                current = self._record(row)
                expires_at = self._parse_time(current.expires_at)
                if current.state == DurableOwnershipState.REVOKED:
                    raise DurableOwnershipConflict("effect ownership is revoked")
                if current.state == DurableOwnershipState.OWNED and expires_at is not None and expires_at > now:
                    raise DurableOwnershipConflict("effect already has an active owner")

                next_version = current.version + 1
                if current.state == DurableOwnershipState.OWNED:
                    conn.execute(
                        "UPDATE effect_ownership SET state=?, owner_id=NULL, expires_at=NULL, version=? WHERE effect_key=?",
                        (DurableOwnershipState.EXPIRED.value, next_version, effect_key),
                    )
                token = current.fencing_token + 1
                conn.execute(
                    """
                    UPDATE effect_ownership
                    SET state=?, owner_id=?, fencing_token=?, version=?, acquired_at=?, expires_at=?
                    WHERE effect_key=?
                    """,
                    (
                        DurableOwnershipState.OWNED.value,
                        owner_id,
                        token,
                        next_version + 1,
                        now_s,
                        expires_s,
                        effect_key,
                    ),
                )
            else:
                token = 1
                conn.execute(
                    """
                    INSERT INTO effect_ownership
                    (effect_key,state,owner_id,fencing_token,version,acquired_at,expires_at)
                    VALUES (?,?,?,?,?,?,?)
                    """,
                    (
                        effect_key,
                        DurableOwnershipState.OWNED.value,
                        owner_id,
                        token,
                        1,
                        now_s,
                        expires_s,
                    ),
                )

            row = conn.execute(
                "SELECT effect_key,state,owner_id,fencing_token,version,acquired_at,expires_at "
                "FROM effect_ownership WHERE effect_key=?",
                (effect_key,),
            ).fetchone()
            assert row is not None
            conn.commit()
            return self._record(row)

    def _current_row(self, conn: sqlite3.Connection, effect_key: str) -> tuple:
        row = conn.execute(
            "SELECT effect_key,state,owner_id,fencing_token,version,acquired_at,expires_at "
            "FROM effect_ownership WHERE effect_key=?",
            (effect_key,),
        ).fetchone()
        if row is None:
            raise KeyError(effect_key)
        return row

    def assert_current(self, effect_key: str, owner_id: str, fencing_token: int) -> DurableOwnershipRecord:
        with self._connect() as conn:
            current = self._record(self._current_row(conn, effect_key))
            self._require_current(current, owner_id, fencing_token)
            return current

    def release(self, effect_key: str, owner_id: str, fencing_token: int) -> DurableOwnershipRecord:
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            current = self._record(self._current_row(conn, effect_key))
            self._require_current(current, owner_id, fencing_token)
            conn.execute(
                "UPDATE effect_ownership SET state=?, owner_id=NULL, expires_at=NULL, version=version+1 WHERE effect_key=?",
                (DurableOwnershipState.RELEASED.value, effect_key),
            )
            conn.commit()
            return self._record(self._current_row(conn, effect_key))

    def renew(self, effect_key: str, owner_id: str, fencing_token: int, ttl: timedelta) -> DurableOwnershipRecord:
        self._validate_ttl(ttl)
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            current = self._record(self._current_row(conn, effect_key))
            self._require_current(current, owner_id, fencing_token)
            conn.execute(
                "UPDATE effect_ownership SET expires_at=?, version=version+1 WHERE effect_key=?",
                ((self._now() + ttl).isoformat(), effect_key),
            )
            conn.commit()
            return self._record(self._current_row(conn, effect_key))

    def revoke(self, effect_key: str) -> DurableOwnershipRecord:
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                current = self._record(self._current_row(conn, effect_key))
            except KeyError:
                current = None
            if current is None:
                conn.execute(
                    "INSERT INTO effect_ownership VALUES (?,?,?,?,?,?,?)",
                    (effect_key, DurableOwnershipState.REVOKED.value, None, 0, 1, None, None),
                )
            else:
                conn.execute(
                    "UPDATE effect_ownership SET state=?, owner_id=NULL, expires_at=NULL, version=version+1 WHERE effect_key=?",
                    (DurableOwnershipState.REVOKED.value, effect_key),
                )
            conn.commit()
            return self._record(self._current_row(conn, effect_key))

    def current(self, effect_key: str) -> DurableOwnershipRecord:
        with self._connect() as conn:
            current = self._record(self._current_row(conn, effect_key))
            expires_at = self._parse_time(current.expires_at)
            if current.state == DurableOwnershipState.OWNED and expires_at is not None and expires_at <= self._now():
                conn.execute("BEGIN IMMEDIATE")
                conn.execute(
                    "UPDATE effect_ownership SET state=?, owner_id=NULL, expires_at=NULL, version=version+1 WHERE effect_key=? AND state=?",
                    (DurableOwnershipState.EXPIRED.value, effect_key, DurableOwnershipState.OWNED.value),
                )
                conn.commit()
                current = self._record(self._current_row(conn, effect_key))
            return current

    @classmethod
    def _require_current(
        cls,
        record: DurableOwnershipRecord,
        owner_id: str,
        fencing_token: int,
    ) -> None:
        expires_at = cls._parse_time(record.expires_at)
        if record.state != DurableOwnershipState.OWNED:
            raise DurableStaleOwner(f"effect is not owned: {record.state}")
        if expires_at is not None and expires_at <= cls._now():
            raise DurableStaleOwner("ownership has expired")
        if record.owner_id != owner_id or record.fencing_token != fencing_token:
            raise DurableStaleOwner("stale owner or fencing token")
