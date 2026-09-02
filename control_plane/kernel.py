"""Deterministic, local-only Control Plane kernel primitives."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from hashlib import sha256
from threading import Lock
from types import MappingProxyType
from typing import FrozenSet, Mapping, Optional
from uuid import uuid4

from .target_identity import TargetIdentity


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _digest(parts: tuple[str, ...]) -> str:
    return sha256("|".join(parts).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EngagementPolicy:
    engagement_id: str
    authorized_targets: FrozenSet[str]
    allowed_actions: FrozenSet[str]
    policy_version: str
    expires_at: datetime
    max_budget: Decimal


@dataclass(frozen=True)
class Capability:
    capability_id: str
    engagement_id: str
    principal_id: str
    target_set: FrozenSet[str]
    allowed_actions: FrozenSet[str]
    expires_at: datetime
    policy_version: str
    risk_class: str = "R0"
    revoked: bool = False

    def revoke(self) -> "Capability":
        return replace(self, revoked=True)


@dataclass(frozen=True)
class Action:
    action_id: str
    principal_id: str
    target: str
    action_type: str
    effect_key: str
    target_identity_digest: str
    requested_at: datetime = field(default_factory=now_utc)

    def digest(self) -> str:
        return _digest(
            (
                self.action_id,
                self.principal_id,
                self.target,
                self.action_type,
                self.effect_key,
                self.target_identity_digest,
            )
        )


@dataclass(frozen=True)
class Lease:
    lease_id: str
    action_id: str
    action_digest: str
    capability_id: str
    engagement_id: str
    target: str
    target_identity_digest: str
    action_type: str
    effect_key: str
    policy_version: str
    issued_at: datetime
    expires_at: datetime
    budget_reservation: Decimal
    consumed: bool = False
    revoked: bool = False

    def revoke(self) -> "Lease":
        return replace(self, revoked=True)


@dataclass(frozen=True)
class TrajectoryState:
    trajectory_id: str
    engagement_id: str
    status: str = "ACTIVE"
    sequence: int = 0
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ProvenanceEvent:
    event_id: str
    event_type: str
    payload: Mapping[str, str]
    previous_hash: str
    event_hash: str
    recorded_at: datetime


class BudgetGovernor:
    """Thread-safe pessimistic reservation ledger."""

    def __init__(self, ceiling: Decimal) -> None:
        if ceiling < 0:
            raise ValueError("budget ceiling must be non-negative")
        self._ceiling = ceiling
        self._reserved = Decimal("0")
        self._consumed = Decimal("0")
        self._lock = Lock()

    @property
    def reserved(self) -> Decimal:
        with self._lock:
            return self._reserved

    @property
    def consumed(self) -> Decimal:
        with self._lock:
            return self._consumed

    def reserve(self, amount: Decimal) -> None:
        if amount < 0:
            raise ValueError("reservation must be non-negative")
        with self._lock:
            available = self._ceiling - self._reserved - self._consumed
            if amount > available:
                raise PermissionError("budget reservation denied")
            self._reserved += amount

    def release(self, amount: Decimal) -> None:
        if amount < 0:
            raise ValueError("release must be non-negative")
        with self._lock:
            if amount > self._reserved:
                raise ValueError("cannot release more than reserved")
            self._reserved -= amount

    def consume(self, amount: Decimal, reservation: Optional[Decimal] = None) -> None:
        if amount < 0:
            raise ValueError("consumption must be non-negative")
        with self._lock:
            if reservation is not None:
                if reservation > self._reserved:
                    raise ValueError("reservation exceeds outstanding reservation")
                self._reserved -= reservation
            available = self._ceiling - self._reserved - self._consumed
            if amount > available:
                raise PermissionError("budget consumption denied")
            self._consumed += amount


class KillSwitch:
    """Independent stop state for local kernel tests."""

    def __init__(self) -> None:
        self._engagements: set[str] = set()
        self._lock = Lock()

    def trip(self, engagement_id: str) -> None:
        with self._lock:
            self._engagements.add(engagement_id)

    def is_tripped(self, engagement_id: str) -> bool:
        with self._lock:
            return engagement_id in self._engagements


class ProvenanceLedger:
    """Hash-linked provenance chain with immutable event payloads."""

    def __init__(self) -> None:
        self._events: list[ProvenanceEvent] = []
        self._lock = Lock()

    @property
    def events(self) -> tuple[ProvenanceEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def append(self, event_type: str, payload: Mapping[str, str]) -> ProvenanceEvent:
        with self._lock:
            normalized = dict(sorted(payload.items()))
            canonical = "|".join(f"{k}={v}" for k, v in normalized.items())
            previous = self._events[-1].event_hash if self._events else "GENESIS"
            digest = _digest((previous, event_type, canonical))
            event = ProvenanceEvent(
                event_id=str(uuid4()),
                event_type=event_type,
                payload=MappingProxyType(normalized),
                previous_hash=previous,
                event_hash=digest,
                recorded_at=now_utc(),
            )
            self._events.append(event)
            return event

    def verify(self) -> bool:
        with self._lock:
            previous = "GENESIS"
            for event in self._events:
                canonical = "|".join(
                    f"{k}={event.payload[k]}" for k in sorted(event.payload)
                )
                expected = _digest((previous, event.event_type, canonical))
                if event.previous_hash != previous or event.event_hash != expected:
                    return False
                previous = event.event_hash
            return True


class ControlPlane:
    """Fail-closed authorization kernel for local fixtures."""

    def __init__(
        self,
        policy: EngagementPolicy,
        governor: BudgetGovernor,
        kill_switch: KillSwitch,
        ledger: ProvenanceLedger,
    ) -> None:
        self.policy = policy
        self.governor = governor
        self.kill_switch = kill_switch
        self.ledger = ledger
        self._capabilities: dict[str, Capability] = {}
        self._leases: dict[str, Lease] = {}
        self._effect_keys: dict[str, str] = {}
        self._trajectories: dict[str, TrajectoryState] = {}
        self._lock = Lock()

    def register_capability(self, capability: Capability) -> None:
        if capability.engagement_id != self.policy.engagement_id:
            raise PermissionError("capability belongs to another engagement")
        if capability.policy_version != self.policy.policy_version:
            raise PermissionError("capability policy version mismatch")
        with self._lock:
            self._capabilities[capability.capability_id] = capability

    def get_lease(self, lease_id: str) -> Lease:
        with self._lock:
            lease = self._leases.get(lease_id)
            if lease is None:
                raise PermissionError("unknown lease")
            return lease

    def revoke_capability(self, capability_id: str) -> None:
        with self._lock:
            capability = self._capabilities.get(capability_id)
            if capability is None:
                raise KeyError(capability_id)
            self._capabilities[capability_id] = capability.revoke()
            for lease_id, lease in self._leases.items():
                if lease.capability_id == capability_id and not lease.consumed:
                    self._leases[lease_id] = lease.revoke()
            self.ledger.append("CAPABILITY_REVOKED", {"capability_id": capability_id})

    def register_trajectory(self, trajectory_id: Optional[str] = None) -> TrajectoryState:
        trajectory = TrajectoryState(
            trajectory_id=trajectory_id or str(uuid4()),
            engagement_id=self.policy.engagement_id,
        )
        with self._lock:
            self._trajectories[trajectory.trajectory_id] = trajectory
        return trajectory

    def authorize(
        self,
        action: Action,
        capability_id: str,
        target_identity: TargetIdentity,
        reservation: Decimal,
        lease_ttl_seconds: int = 30,
    ) -> Lease:
        now = now_utc()
        observed_digest = target_identity.digest()
        if observed_digest != action.target_identity_digest:
            raise PermissionError("target identity binding mismatch")
        if lease_ttl_seconds <= 0:
            raise ValueError("lease TTL must be positive")
        with self._lock:
            if self.kill_switch.is_tripped(self.policy.engagement_id):
                raise PermissionError("engagement kill switch is active")
            if now >= self.policy.expires_at:
                raise PermissionError("engagement policy expired")
            capability = self._capabilities.get(capability_id)
            if capability is None or capability.revoked:
                raise PermissionError("capability unavailable")
            if capability.policy_version != self.policy.policy_version:
                raise PermissionError("capability policy version mismatch")
            if capability.principal_id != action.principal_id:
                raise PermissionError("principal mismatch")
            if now >= capability.expires_at:
                raise PermissionError("capability expired")
            if action.target != target_identity.canonical_target:
                raise PermissionError("target identity canonical-target mismatch")
            if action.target not in self.policy.authorized_targets:
                raise PermissionError("target out of scope")
            if action.target not in capability.target_set:
                raise PermissionError("target not delegated")
            if action.action_type not in self.policy.allowed_actions:
                raise PermissionError("action not allowed by policy")
            if action.action_type not in capability.allowed_actions:
                raise PermissionError("action not delegated")
            if action.effect_key in self._effect_keys:
                raise PermissionError("duplicate effect identity")
            if reservation < 0:
                raise ValueError("reservation must be non-negative")
            self.governor.reserve(reservation)
            expiry = min(self.policy.expires_at, capability.expires_at)
            lease_expiry = min(expiry, now + timedelta(seconds=lease_ttl_seconds))
            lease = Lease(
                lease_id=str(uuid4()),
                action_id=action.action_id,
                action_digest=action.digest(),
                capability_id=capability.capability_id,
                engagement_id=self.policy.engagement_id,
                target=action.target,
                target_identity_digest=observed_digest,
                action_type=action.action_type,
                effect_key=action.effect_key,
                policy_version=self.policy.policy_version,
                issued_at=now,
                expires_at=lease_expiry,
                budget_reservation=reservation,
            )
            self._leases[lease.lease_id] = lease
            self._effect_keys[action.effect_key] = lease.lease_id
            self.ledger.append(
                "LEASE_ISSUED",
                {
                    "lease_id": lease.lease_id,
                    "action_id": action.action_id,
                    "action_digest": lease.action_digest,
                    "capability_id": capability.capability_id,
                    "target": action.target,
                    "target_identity_digest": observed_digest,
                    "action_type": action.action_type,
                    "policy_version": self.policy.policy_version,
                },
            )
            return lease

    def consume_lease(self, lease_id: str, actual_cost: Decimal) -> Lease:
        now = now_utc()
        with self._lock:
            lease = self._leases.get(lease_id)
            if lease is None:
                raise PermissionError("unknown lease")
            if lease.consumed or lease.revoked:
                raise PermissionError("lease unavailable")
            if now >= lease.expires_at:
                raise PermissionError("lease expired")
            if self.kill_switch.is_tripped(lease.engagement_id):
                raise PermissionError("engagement kill switch is active")
            if actual_cost < 0 or actual_cost > lease.budget_reservation:
                raise PermissionError("actual cost exceeds reserved budget")
            self.governor.consume(actual_cost, reservation=lease.budget_reservation)
            updated = replace(lease, consumed=True)
            self._leases[lease_id] = updated
            self.ledger.append(
                "LEASE_CONSUMED",
                {"lease_id": lease_id, "actual_cost": str(actual_cost)},
            )
            return updated

    def abort_lease(self, lease_id: str) -> Lease:
        with self._lock:
            lease = self._leases.get(lease_id)
            if lease is None:
                raise KeyError(lease_id)
            if not lease.consumed and lease.budget_reservation:
                self.governor.release(lease.budget_reservation)
            updated = replace(lease, revoked=True)
            self._leases[lease_id] = updated
            self.ledger.append("LEASE_ABORTED", {"lease_id": lease_id})
            return updated
