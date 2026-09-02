from datetime import timedelta
from decimal import Decimal

import pytest

from control_plane.kernel import (
    Action,
    BudgetGovernor,
    Capability,
    ControlPlane,
    EngagementPolicy,
    KillSwitch,
    ProvenanceLedger,
    now_utc,
)
from control_plane.target_identity import TargetIdentity


def make_identity(target="fixture.local", endpoint="127.0.0.1", digest="dns-1"):
    return TargetIdentity(
        canonical_target=target,
        endpoint=endpoint,
        protocol="https",
        port=443,
        resolution_evidence_digest=digest,
        observed_at=now_utc(),
    )


def make_kernel():
    now = now_utc()
    policy = EngagementPolicy(
        engagement_id="eng-1",
        authorized_targets=frozenset({"fixture.local"}),
        allowed_actions=frozenset({"READ"}),
        policy_version="p1",
        expires_at=now + timedelta(minutes=5),
        max_budget=Decimal("10.00"),
    )
    return ControlPlane(policy, BudgetGovernor(policy.max_budget), KillSwitch(), ProvenanceLedger())


def make_capability(kernel):
    kernel.register_capability(
        Capability(
            capability_id="cap-1",
            engagement_id="eng-1",
            principal_id="worker-1",
            target_set=frozenset({"fixture.local"}),
            allowed_actions=frozenset({"READ"}),
            expires_at=kernel.policy.expires_at,
            policy_version="p1",
        )
    )


def make_action(identity, key="effect-1", target="fixture.local"):
    return Action(
        action_id=f"action-{key}",
        principal_id="worker-1",
        target=target,
        action_type="READ",
        effect_key=key,
        target_identity_digest=identity.digest(),
    )


def test_authorization_issues_lease_and_reserves_budget():
    kernel = make_kernel()
    make_capability(kernel)
    identity = make_identity()
    lease = kernel.authorize(make_action(identity), "cap-1", identity, Decimal("1.50"))
    assert lease.target == "fixture.local"
    assert lease.target_identity_digest == identity.digest()
    assert lease.action_digest == make_action(identity).digest()
    assert kernel.governor.reserved == Decimal("1.50")
    assert kernel.ledger.verify()


def test_out_of_scope_fails_closed():
    kernel = make_kernel()
    make_capability(kernel)
    identity = make_identity(target="outside.local")
    with pytest.raises(PermissionError, match="out of scope"):
        kernel.authorize(make_action(identity, target="outside.local"), "cap-1", identity, Decimal("1"))
    assert kernel.governor.reserved == Decimal("0")


def test_target_identity_change_is_rejected():
    kernel = make_kernel()
    make_capability(kernel)
    original = make_identity(endpoint="127.0.0.1", digest="dns-1")
    changed = make_identity(endpoint="127.0.0.2", digest="dns-2")
    action = make_action(original)
    with pytest.raises(PermissionError, match="target identity binding"):
        kernel.authorize(action, "cap-1", changed, Decimal("1"))
    assert kernel.governor.reserved == Decimal("0")


def test_revocation_invalidates_active_leases():
    kernel = make_kernel()
    make_capability(kernel)
    identity = make_identity()
    lease = kernel.authorize(make_action(identity), "cap-1", identity, Decimal("1"))
    kernel.revoke_capability("cap-1")
    with pytest.raises(PermissionError, match="lease unavailable"):
        kernel.consume_lease(lease.lease_id, Decimal("0.50"))


def test_kill_switch_blocks_new_authorization_and_consumption():
    kernel = make_kernel()
    make_capability(kernel)
    identity = make_identity()
    lease = kernel.authorize(make_action(identity), "cap-1", identity, Decimal("1"))
    kernel.kill_switch.trip("eng-1")
    with pytest.raises(PermissionError, match="kill switch"):
        kernel.authorize(make_action(identity, "effect-2"), "cap-1", identity, Decimal("1"))
    with pytest.raises(PermissionError, match="kill switch"):
        kernel.consume_lease(lease.lease_id, Decimal("1"))


def test_duplicate_effect_identity_is_rejected_before_second_reservation():
    kernel = make_kernel()
    make_capability(kernel)
    identity = make_identity()
    kernel.authorize(make_action(identity), "cap-1", identity, Decimal("2"))
    with pytest.raises(PermissionError, match="duplicate effect"):
        kernel.authorize(make_action(identity), "cap-1", identity, Decimal("3"))
    assert kernel.governor.reserved == Decimal("2")


def test_budget_reservation_is_pessimistic_and_atomic():
    kernel = make_kernel()
    make_capability(kernel)
    identity = make_identity()
    kernel.authorize(make_action(identity, "a"), "cap-1", identity, Decimal("6"))
    with pytest.raises(PermissionError, match="budget reservation"):
        kernel.authorize(make_action(identity, "b"), "cap-1", identity, Decimal("5"))
    assert kernel.governor.reserved == Decimal("6")


def test_actual_cost_cannot_exceed_lease_reservation():
    kernel = make_kernel()
    make_capability(kernel)
    identity = make_identity()
    lease = kernel.authorize(make_action(identity), "cap-1", identity, Decimal("2"))
    with pytest.raises(PermissionError, match="reserved budget"):
        kernel.consume_lease(lease.lease_id, Decimal("3"))
    assert kernel.governor.reserved == Decimal("2")


def test_lease_consumption_moves_reservation_to_consumed_budget():
    kernel = make_kernel()
    make_capability(kernel)
    identity = make_identity()
    lease = kernel.authorize(make_action(identity), "cap-1", identity, Decimal("2"))
    consumed = kernel.consume_lease(lease.lease_id, Decimal("1.25"))
    assert consumed.consumed is True
    assert kernel.governor.reserved == Decimal("0")
    assert kernel.governor.consumed == Decimal("1.25")


def test_provenance_payload_is_immutable():
    kernel = make_kernel()
    event = kernel.ledger.append("A", {"x": "1"})
    with pytest.raises(TypeError):
        event.payload["x"] = "tampered"
    assert kernel.ledger.verify() is True
