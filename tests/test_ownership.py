from datetime import datetime, timedelta, timezone
from threading import Barrier
from concurrent.futures import ThreadPoolExecutor

import pytest

from control_plane.ownership import (
    OwnershipAuthority,
    OwnershipConflict,
    OwnershipState,
    StaleOwner,
)


class FakeClock:
    def __init__(self) -> None:
        self.value = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.value

    def advance(self, seconds: int) -> None:
        self.value += timedelta(seconds=seconds)


def test_simultaneous_claim_has_one_winner() -> None:
    authority = OwnershipAuthority()
    barrier = Barrier(8)

    def claim(worker: int):
        barrier.wait()
        try:
            return ("winner", authority.claim("effect-1", f"worker-{worker}", timedelta(seconds=30)))
        except OwnershipConflict:
            return ("loser", None)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(claim, range(8)))

    winners = [result for result in results if result[0] == "winner"]
    assert len(winners) == 1
    assert authority.current("effect-1").state == OwnershipState.OWNED


def test_stale_fencing_token_is_rejected_after_expiry() -> None:
    clock = FakeClock()
    authority = OwnershipAuthority(now=clock)

    first = authority.claim("effect-1", "worker-a", timedelta(seconds=5))
    clock.advance(5)
    second = authority.claim("effect-1", "worker-b", timedelta(seconds=5))

    assert second.fencing_token > first.fencing_token
    with pytest.raises(StaleOwner):
        authority.assert_current("effect-1", "worker-a", first.fencing_token)
    authority.assert_current("effect-1", "worker-b", second.fencing_token)


def test_duplicate_active_claim_does_not_create_second_owner() -> None:
    authority = OwnershipAuthority()
    first = authority.claim("effect-1", "worker-a", timedelta(seconds=30))

    with pytest.raises(OwnershipConflict):
        authority.claim("effect-1", "worker-b", timedelta(seconds=30))

    current = authority.current("effect-1")
    assert current.owner_id == "worker-a"
    assert current.fencing_token == first.fencing_token


def test_renew_requires_current_fencing_token() -> None:
    authority = OwnershipAuthority()
    first = authority.claim("effect-1", "worker-a", timedelta(seconds=30))

    with pytest.raises(StaleOwner):
        authority.renew("effect-1", "worker-b", first.fencing_token, timedelta(seconds=30))

    renewed = authority.renew("effect-1", "worker-a", first.fencing_token, timedelta(seconds=60))
    assert renewed.version > first.version
    assert renewed.fencing_token == first.fencing_token


def test_release_allows_new_owner_with_new_fencing_token() -> None:
    authority = OwnershipAuthority()
    first = authority.claim("effect-1", "worker-a", timedelta(seconds=30))
    released = authority.release("effect-1", "worker-a", first.fencing_token)
    second = authority.claim("effect-1", "worker-b", timedelta(seconds=30))

    assert released.state == OwnershipState.RELEASED
    assert second.owner_id == "worker-b"
    assert second.fencing_token > first.fencing_token


def test_revocation_blocks_future_claims() -> None:
    authority = OwnershipAuthority()
    first = authority.claim("effect-1", "worker-a", timedelta(seconds=30))
    revoked = authority.revoke("effect-1")

    assert revoked.state == OwnershipState.REVOKED
    with pytest.raises(OwnershipConflict):
        authority.claim("effect-1", "worker-b", timedelta(seconds=30))
    with pytest.raises(StaleOwner):
        authority.assert_current("effect-1", "worker-a", first.fencing_token)


def test_claim_after_expiry_is_recovery_not_double_ownership() -> None:
    clock = FakeClock()
    authority = OwnershipAuthority(now=clock)

    first = authority.claim("effect-1", "crashed-worker", timedelta(seconds=5))
    clock.advance(6)
    assert authority.current("effect-1").state == OwnershipState.EXPIRED

    recovered = authority.claim("effect-1", "recovery-worker", timedelta(seconds=30))
    assert recovered.fencing_token > first.fencing_token
    assert recovered.owner_id == "recovery-worker"
    with pytest.raises(StaleOwner):
        authority.assert_current("effect-1", "crashed-worker", first.fencing_token)


def test_invalid_ttl_is_rejected() -> None:
    authority = OwnershipAuthority()
    with pytest.raises(ValueError):
        authority.claim("effect-1", "worker-a", timedelta(0))
