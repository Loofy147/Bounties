from decimal import Decimal

import pytest

from control_plane.effects import EffectLedger, EffectState, LocalEffectProtocol
from control_plane.kernel import Action
from tests.test_control_plane_kernel import make_capability, make_kernel


def authorize_effect():
    kernel = make_kernel()
    make_capability(kernel)
    lease = kernel.authorize(
        Action(
            action_id="a1",
            principal_id="worker-1",
            target="fixture.local",
            action_type="READ",
            effect_key="effect-1",
        ),
        "cap-1",
        Decimal("2"),
    )
    protocol = LocalEffectProtocol(kernel, EffectLedger())
    return protocol, lease


def test_effect_lifecycle_requires_prepare_before_commit():
    protocol, lease = authorize_effect()
    protocol.authorize_effect(lease)

    with pytest.raises(PermissionError, match="invalid effect transition"):
        protocol.mark_committed("effect-1", "result")

    assert protocol.prepare("effect-1").state == EffectState.PREPARED
    assert protocol.mark_committed("effect-1", "result").state == EffectState.COMMITTED


def test_unknown_outcome_is_terminal_until_external_reconciliation():
    protocol, lease = authorize_effect()
    protocol.authorize_effect(lease)
    protocol.prepare("effect-1")

    unknown = protocol.mark_unknown("effect-1")
    assert unknown.state == EffectState.UNKNOWN

    with pytest.raises(RuntimeError, match="external reconciliation required"):
        protocol.recover_unknown("effect-1")


def test_failed_effect_cannot_be_committed_afterward():
    protocol, lease = authorize_effect()
    protocol.authorize_effect(lease)
    protocol.prepare("effect-1")
    assert protocol.mark_failed("effect-1").state == EffectState.FAILED

    with pytest.raises(PermissionError, match="invalid effect transition"):
        protocol.mark_committed("effect-1", "result")


def test_duplicate_effect_registration_is_rejected():
    protocol, lease = authorize_effect()
    protocol.authorize_effect(lease)

    with pytest.raises(PermissionError, match="duplicate effect identity"):
        protocol.authorize_effect(lease)
