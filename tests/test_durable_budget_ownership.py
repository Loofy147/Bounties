from datetime import timedelta
from decimal import Decimal
from multiprocessing import get_context

import pytest

from control_plane.durable_budget_ownership import (
    AtomicAdmissionConflict,
    AtomicStaleOwner,
    SQLiteAtomicAuthority,
)


def _claim_worker(path: str, result_queue, owner_id: str) -> None:
    authority = SQLiteAtomicAuthority(path, "engagement-A", Decimal("10"))
    try:
        record = authority.claim("effect-1", owner_id, Decimal("6"), timedelta(seconds=30))
        result_queue.put((owner_id, "won", record.fencing_token))
    except AtomicAdmissionConflict:
        result_queue.put((owner_id, "lost", None))


def test_ownership_and_budget_are_admitted_together(tmp_path):
    path = tmp_path / "authority.sqlite3"
    authority = SQLiteAtomicAuthority(path, "engagement-A", Decimal("10"))

    record = authority.claim("effect-1", "worker-A", Decimal("6"), timedelta(seconds=30))
    assert record.owner_id == "worker-A"
    assert record.reservation == Decimal("6")
    assert authority.budget() == (Decimal("10"), Decimal("6"), Decimal("0"))

    with pytest.raises(AtomicAdmissionConflict):
        authority.claim("effect-2", "worker-B", Decimal("5"), timedelta(seconds=30))

    # The failed claim must not reserve budget or create ownership for effect-2.
    assert authority.budget() == (Decimal("10"), Decimal("6"), Decimal("0"))


def test_release_returns_ownership_and_reservation_atomically(tmp_path):
    path = tmp_path / "authority.sqlite3"
    authority = SQLiteAtomicAuthority(path, "engagement-A", Decimal("10"))
    record = authority.claim("effect-1", "worker-A", Decimal("6"), timedelta(seconds=30))

    released = authority.release("effect-1", "worker-A", record.fencing_token)
    assert released.state == "RELEASED"
    assert authority.budget() == (Decimal("10"), Decimal("0"), Decimal("0"))


def test_concurrent_process_claims_have_one_winner_and_one_reservation(tmp_path):
    path = tmp_path / "authority.sqlite3"
    # Initialize once so all workers use the same persistent budget record.
    SQLiteAtomicAuthority(path, "engagement-A", Decimal("6"))

    ctx = get_context("spawn")
    queue = ctx.Queue()
    processes = [
        ctx.Process(target=_claim_worker, args=(str(path), queue, f"worker-{i}"))
        for i in range(2)
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=15)
        assert process.exitcode == 0

    results = [queue.get(timeout=5) for _ in processes]
    assert sum(status == "won" for _, status, _ in results) == 1
    assert sum(status == "lost" for _, status, _ in results) == 1

    authority = SQLiteAtomicAuthority(path, "engagement-A", Decimal("6"))
    ceiling, reserved, consumed = authority.budget()
    assert (ceiling, reserved, consumed) == (Decimal("6"), Decimal("6"), Decimal("0"))


def test_stale_owner_cannot_release_after_expiry_recovery(tmp_path):
    path = tmp_path / "authority.sqlite3"
    authority = SQLiteAtomicAuthority(path, "engagement-A", Decimal("20"))
    first = authority.claim("effect-1", "worker-A", Decimal("5"), timedelta(microseconds=1))

    # A tiny delay is enough to cross the expiry boundary without injecting a
    # clock dependency into the durable implementation.
    import time
    time.sleep(0.01)

    second = authority.claim("effect-1", "worker-B", Decimal("7"), timedelta(seconds=30))
    assert second.fencing_token > first.fencing_token
    assert second.owner_id == "worker-B"
    assert authority.budget() == (Decimal("20"), Decimal("7"), Decimal("0"))

    with pytest.raises(AtomicStaleOwner):
        authority.release("effect-1", "worker-A", first.fencing_token)


def test_stale_owner_cannot_validate_after_recovery(tmp_path):
    path = tmp_path / "authority.sqlite3"
    authority = SQLiteAtomicAuthority(path, "engagement-A", Decimal("20"))
    first = authority.claim("effect-1", "worker-A", Decimal("5"), timedelta(seconds=30))

    # Force a new owner through explicit release, then verify the old fence is dead.
    authority.release("effect-1", "worker-A", first.fencing_token)
    second = authority.claim("effect-1", "worker-B", Decimal("5"), timedelta(seconds=30))
    assert second.fencing_token > first.fencing_token

    with pytest.raises(AtomicStaleOwner):
        authority.assert_current("effect-1", "worker-A", first.fencing_token)
