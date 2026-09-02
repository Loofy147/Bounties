"""Local Policy Enforcement Point for deterministic lease binding tests."""

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
    action_digest: str
    target_identity_digest: str
    actual_cost: Decimal


class LocalPEP:
    """Fail-closed local PEP; performs no external I/O."""

    def __init__(self, control_plane: ControlPlane) -> None:
        self.control_plane = control_plane

    def validate_binding(self, request: ExecutionRequest, lease: Lease) -> None:
        checks = (
            (request.lease_id == lease.lease_id, "lease binding mismatch"),
            (request.target == lease.target, "target binding mismatch"),
            (request.action_type == lease.action_type, "action binding mismatch"),
            (request.effect_key == lease.effect_key, "effect binding mismatch"),
            (request.action_digest == lease.action_digest, "action digest mismatch"),
            (
                request.target_identity_digest == lease.target_identity_digest,
                "target identity digest mismatch",
            ),
        )
        for valid, message in checks:
            if not valid:
                raise PermissionError(message)

    def execute(self, request: ExecutionRequest) -> Lease:
        """Admit one exact lease into the local execution boundary.

        No network or target-side effect occurs here. A future external
        executor must provide a durable effect protocol for crash/commit
        ambiguity before this adapter can become a real execution PEP.
        """
        lease = self.control_plane.get_lease(request.lease_id)
        self.validate_binding(request, lease)
        return self.control_plane.consume_lease(request.lease_id, request.actual_cost)
