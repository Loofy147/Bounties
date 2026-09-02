"""Typed, deterministic target identity for the local control-plane kernel."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256


@dataclass(frozen=True)
class TargetIdentity:
    """Identity snapshot captured at authorization time.

    This intentionally represents *observed identity*, not merely the logical
    hostname. A future resolver can populate stronger endpoint evidence.
    """

    canonical_target: str
    endpoint: str
    protocol: str
    port: int
    resolution_evidence_digest: str
    observed_at: datetime

    def digest(self) -> str:
        canonical = "|".join(
            (
                self.canonical_target,
                self.endpoint,
                self.protocol,
                str(self.port),
                self.resolution_evidence_digest,
                self.observed_at.astimezone(timezone.utc).isoformat(),
            )
        )
        return sha256(canonical.encode("utf-8")).hexdigest()
