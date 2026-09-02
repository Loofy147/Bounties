"""Deterministic Hunter v0.1 execution kernel.

This module deliberately contains no target-specific exploit logic. It provides
scope enforcement, immutable experiment records, hash-linked evidence, and a
separate validation gate for local/authorized security research.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from hashlib import sha256
import json
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class ScopeContract:
    target_id: str
    version: str
    allowed_assets: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    environment: str
    max_steps: int = 100

    def permits(self, asset: str, action: str) -> bool:
        return asset in self.allowed_assets and action in self.allowed_actions


@dataclass(frozen=True)
class Experiment:
    hypothesis_id: str
    asset: str
    action: str
    inputs: dict[str, Any]
    seed: int = 0


@dataclass(frozen=True)
class Evidence:
    hypothesis_id: str
    target_version: str
    expected: Any
    observed: Any
    trace: tuple[dict[str, Any], ...]
    artifacts: tuple[str, ...] = ()
    parent_hash: str | None = None

    def digest(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Validation:
    real: bool
    reachable: bool
    security_property_violated: bool
    impact_demonstrated: bool
    reproducible: bool
    scope_confirmed: bool
    novelty_checked: bool
    notes: str = ""

    @property
    def submission_ready(self) -> bool:
        return all(
            (
                self.real,
                self.reachable,
                self.security_property_violated,
                self.impact_demonstrated,
                self.reproducible,
                self.scope_confirmed,
                self.novelty_checked,
            )
        )


@dataclass
class HunterKernel:
    scope: ScopeContract
    evidence_chain: list[str] = field(default_factory=list)

    def plan(self, experiment: Experiment) -> None:
        if not self.scope.permits(experiment.asset, experiment.action):
            raise PermissionError(
                f"experiment denied by scope: asset={experiment.asset!r}, action={experiment.action!r}"
            )
        if len(experiment.inputs) > self.scope.max_steps:
            raise ValueError("experiment exceeds configured input budget")

    def execute(
        self,
        experiment: Experiment,
        runner: Callable[[Experiment], tuple[Any, Iterable[dict[str, Any]]]],
    ) -> Evidence:
        self.plan(experiment)
        observed, trace = runner(experiment)
        evidence = Evidence(
            hypothesis_id=experiment.hypothesis_id,
            target_version=self.scope.version,
            expected=experiment.inputs.get("expected"),
            observed=observed,
            trace=tuple(dict(item) for item in trace),
            parent_hash=self.evidence_chain[-1] if self.evidence_chain else None,
        )
        self.evidence_chain.append(evidence.digest())
        return evidence


def deterministic_runner(
    fn: Callable[[dict[str, Any], int], Any]
) -> Callable[[Experiment], tuple[Any, Iterable[dict[str, Any]]]]:
    """Adapt a pure deterministic function to the evidence-producing interface."""
    def run(experiment: Experiment) -> tuple[Any, Iterable[dict[str, Any]]]:
        observed = fn(experiment.inputs, experiment.seed)
        yield_trace = ({"seed": experiment.seed, "inputs": experiment.inputs},)
        return observed, yield_trace

    return run


__all__ = [
    "Evidence",
    "Experiment",
    "HunterKernel",
    "ScopeContract",
    "Validation",
    "deterministic_runner",
]
