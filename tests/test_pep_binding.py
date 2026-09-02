from decimal import Decimal

import pytest

from control_plane.pep import ExecutionRequest, LocalPEP
from tests.test_control_plane_kernel import make_action, make_capability, make_kernel


def test_pep_accepts_exact_lease_binding():
    kernel = make_kernel()
    make_capability(kernel)
    lease = kernel.authorize(make_action(), "cap-1", Decimal("2"))
    pep = LocalPEP(kernel)

    request = ExecutionRequest(
        lease_id=lease.lease_id,
        target=lease.target,
        action_type=lease.action_type,
        effect_key=lease.effect_key,
        observed_target_identity=lease.target,
        actual_cost=Decimal("1"),
    )

    consumed = pep.execute(request)
    assert consumed.consumed is True


def test_pep_rejects_target_mismatch_before_consumption():
    kernel = make_kernel()
    make_capability(kernel)
    lease = kernel.authorize(make_action(), "cap-1", Decimal("2"))
    pep = LocalPEP(kernel)

    request = ExecutionRequest(
        lease_id=lease.lease_id,
        target="other.fixture.local",
        action_type=lease.action_type,
        effect_key=lease.effect_key,
        observed_target_identity=lease.target,
        actual_cost=Decimal("1"),
    )

    with pytest.raises(PermissionError, match="target binding"):
        pep.execute(request)

    assert kernel.governor.reserved == Decimal("2")


def test_pep_rejects_target_identity_mismatch():
    kernel = make_kernel()
    make_capability(kernel)
    lease = kernel.authorize(make_action(), "cap-1", Decimal("2"))
    pep = LocalPEP(kernel)

    request = ExecutionRequest(
        lease_id=lease.lease_id,
        target=lease.target,
        action_type=lease.action_type,
        effect_key=lease.effect_key,
        observed_target_identity="different-identity",
        actual_cost=Decimal("1"),
    )

    with pytest.raises(PermissionError, match="target identity"):
        pep.execute(request)

    assert kernel.governor.reserved == Decimal("2")
