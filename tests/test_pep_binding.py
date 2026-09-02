from decimal import Decimal

import pytest

from control_plane.pep import ExecutionRequest, LocalPEP
from tests.test_control_plane_kernel import make_action, make_capability, make_identity, make_kernel


def make_request(lease, action, cost=Decimal("1")):
    return ExecutionRequest(
        lease_id=lease.lease_id,
        target=lease.target,
        action_type=lease.action_type,
        effect_key=lease.effect_key,
        action_digest=lease.action_digest,
        target_identity_digest=action.target_identity_digest,
        actual_cost=cost,
    )


def test_pep_accepts_exact_lease_binding():
    kernel = make_kernel()
    make_capability(kernel)
    identity = make_identity()
    action = make_action(identity)
    lease = kernel.authorize(action, "cap-1", identity, Decimal("2"))
    consumed = LocalPEP(kernel).execute(make_request(lease, action))
    assert consumed.consumed is True


def test_pep_rejects_target_mismatch_before_consumption():
    kernel = make_kernel()
    make_capability(kernel)
    identity = make_identity()
    action = make_action(identity)
    lease = kernel.authorize(action, "cap-1", identity, Decimal("2"))
    request = make_request(lease, action)
    request = request.__class__(
        **{**request.__dict__, "target": "other.fixture.local"}
    )
    with pytest.raises(PermissionError, match="target binding"):
        LocalPEP(kernel).execute(request)
    assert kernel.governor.reserved == Decimal("2")


def test_pep_rejects_action_digest_mismatch():
    kernel = make_kernel()
    make_capability(kernel)
    identity = make_identity()
    action = make_action(identity)
    lease = kernel.authorize(action, "cap-1", identity, Decimal("2"))
    request = make_request(lease, action)
    request = request.__class__(
        **{**request.__dict__, "action_digest": "forged"}
    )
    with pytest.raises(PermissionError, match="action digest"):
        LocalPEP(kernel).execute(request)
    assert kernel.governor.reserved == Decimal("2")


def test_pep_rejects_target_identity_digest_mismatch():
    kernel = make_kernel()
    make_capability(kernel)
    identity = make_identity()
    action = make_action(identity)
    lease = kernel.authorize(action, "cap-1", identity, Decimal("2"))
    request = make_request(lease, action)
    request = request.__class__(
        **{**request.__dict__, "target_identity_digest": "changed"}
    )
    with pytest.raises(PermissionError, match="target identity digest"):
        LocalPEP(kernel).execute(request)
    assert kernel.governor.reserved == Decimal("2")


def test_pep_rejects_unknown_lease():
    kernel = make_kernel()
    with pytest.raises(PermissionError, match="unknown lease"):
        LocalPEP(kernel).execute(
            ExecutionRequest(
                lease_id="missing",
                target="fixture.local",
                action_type="READ",
                effect_key="effect-1",
                action_digest="x",
                target_identity_digest="y",
                actual_cost=Decimal("1"),
            )
        )
