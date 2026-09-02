"""Local Policy Enforcement Point reference adapter.

No network I/O is performed. The adapter only proves that an execution
request is bound to the exact immutable lease issued by the control plane.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .kernel import ControlPlane, Lease


@dataclass(frozen=True)
class ExecutionRequest:
    lease_id: str
    target: str
    action_type: str
    effect_key: str
    observed_target_identity: str
    actual_cost: Decimal


class LocalPEP:
    """Fail-closed local PEP for execution-binding tests."""

    def __init__(self, control_plane: ControlPlane) -> None:
        self.control_plane = control_plane

    def validate_binding(self, request: ExecutionRequest, lease: Lease) -> None:
        if request.lease_id != lease.lease_id:
            raise PermissionError("lease binding mismatch")
        if request.target != lease.target:
            raise PermissionError("target binding mismatch")
        if request.action_type != lease.action_type:
            raise PermissionError("action binding mismatch")
        if request.effect_key != lease.effect_key:
            raise PermissionError("effect binding mismatch")
        if request.observed_target_identity != lease.target:
            raise PermissionError("target identity mismatch")

    def execute(self, request: ExecutionRequest) -> Lease:
        """Consume exactly one authorized lease after binding verification.

        The method intentionally performs no external side effect. A future
        concrete executor must call this binding gate before dispatching any
        externally visible action.
        """
        lease = self.control_plane._leases.get(request.lease_id)
        if lease is None:
            raise PermissionError("unknown lease")
        self.validate_binding(request, lease)
        return self.control_plane.consume_lease(request.lease_id, request.actual_cost)
