from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from control_plane.durable_ownership import (
    DurableOwnershipConflict,
    DurableOwnershipState,
    DurableStaleOwner,
    SQLiteOwnershipAuthority,
)


def _claim_worker(args: tuple[str, str, str]) -> tuple[str, str, int | None]:
    path, effect_key, owner_id = args
    authority = SQLiteOwnershipAuthority(path)
    try:
        record = authority.claim(effect_key, owner_id, timedelta(seconds=30))
        return ("winner", record.owner_id or "", record.fencing_token)
    except DurableOwnershipConflict:
        return ("loser", owner_id, None)


def _mark_expired(path: str, effect_key: str) -> None:
    expired = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
    import sqlite3

    with sqlite3.connect(path) as conn:
        conn.execute(
            "UPDATE effect_ownership SET expires_at=? WHERE effect_key=?",
            (expired, effect_key),
        )
        conn.commit()


def test_concurrent_process_claim_has_one_winner(tmp_path: Path) -> None:
    path = str(tmp_path / "ownership.sqlite3")
    SQLiteOwnershipAuthority(path)

    args = [(path, "effect-1", f"worker-{i}") for i in range(6)]
    with ProcessPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(_claim_worker, args))

    winners = [result for result in results if result[0] == "winner"]
    losers = [result for result in results if result[0] == "loser"]
    assert len(winners) == 1
    assert len(losers) == 5

    current = SQLiteOwnershipAuthority(path).current("effect-1")
    assert current.state == DurableOwnershipState.OWNED
    assert current.owner_id == winners[0][1]
    assert current.fencing_token == winners[0][2]


def test_expired_owner_is_replaced_by_new_fencing_token(tmp_path: Path) -> None:
    path = str(tmp_path / "ownership.sqlite3")
    authority = SQLiteOwnershipAuthority(path)
    first = authority.claim("effect-1", "worker-a", timedelta(seconds=30))

    _mark_expired(path, "effect-1")
    assert authority.current("effect-1").state == DurableOwnershipState.EXPIRED

    second = authority.claim("effect-1", "worker-b", timedelta(seconds=30))
    assert second.fencing_token > first.fencing_token
    with pytest.raises(DurableStaleOwner):
        authority.assert_current("effect-1", "worker-a", first.fencing_token)


def test_duplicate_registration_never_creates_second_active_owner(tmp_path: Path) -> None:
    path = str(tmp_path / "ownership.sqlite3")
    authority = SQLiteOwnershipAuthority(path)
    first = authority.claim("effect-1", "worker-a", timedelta(seconds=30))

    with pytest.raises(DurableOwnershipConflict):
        SQLiteOwnershipAuthority(path).claim("effect-1", "worker-b", timedelta(seconds=30))

    current = authority.current("effect-1")
    assert current.owner_id == "worker-a"
    assert current.fencing_token == first.fencing_token


def test_revocation_survives_new_authority_instance(tmp_path: Path) -> None:
    path = str(tmp_path / "ownership.sqlite3")
    authority = SQLiteOwnershipAuthority(path)
    first = authority.claim("effect-1", "worker-a", timedelta(seconds=30))
    authority.revoke("effect-1")

    reloaded = SQLiteOwnershipAuthority(path)
    assert reloaded.current("effect-1").state == DurableOwnershipState.REVOKED
    with pytest.raises(DurableOwnershipConflict):
        reloaded.claim("effect-1", "worker-b", timedelta(seconds=30))
    with pytest.raises(DurableStaleOwner):
        reloaded.assert_current("effect-1", "worker-a", first.fencing_token)


def test_renewal_and_release_require_current_fence(tmp_path: Path) -> None:
    path = str(tmp_path / "ownership.sqlite3")
    authority = SQLiteOwnershipAuthority(path)
    first = authority.claim("effect-1", "worker-a", timedelta(seconds=30))

    with pytest.raises(DurableStaleOwner):
        authority.renew("effect-1", "worker-b", first.fencing_token, timedelta(seconds=30))

    renewed = authority.renew("effect-1", "worker-a", first.fencing_token, timedelta(seconds=30))
    assert renewed.fencing_token == first.fencing_token
    released = authority.release("effect-1", "worker-a", renewed.fencing_token)
    assert released.state == DurableOwnershipState.RELEASED
