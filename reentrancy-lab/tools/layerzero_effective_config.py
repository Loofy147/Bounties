#!/usr/bin/env python3
"""Resolve effective LayerZero V2 receive configuration from a deterministic snapshot.

This is intentionally offline: the RPC/event acquisition layer is separate.
The resolver consumes a JSON snapshot containing app-level configuration,
Endpoint library selection, library defaults, and optional historical events.

Rule:
  explicit OApp config wins;
  otherwise selected/default receive library config applies;
  otherwise status is UNRESOLVED.

An empty application-level ULN config is NOT interpreted as zero DVNs.
It is interpreted as "inheritance may apply" until the resolution chain is
complete and provenance is recorded.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class Resolution:
    status: str
    local_eid: int
    remote_eid: int
    oapp: str
    receive_library: str | None
    required_dvns: list[str]
    optional_dvns: list[str]
    optional_threshold: int
    confirmations: int | None
    executor: str | None
    provenance: list[str]
    warnings: list[str]


def _norm_addr(value: str | None) -> str | None:
    return value.lower() if isinstance(value, str) else value


def _non_empty(value: Any) -> bool:
    return value is not None and value != [] and value != ""


def resolve(snapshot: dict[str, Any]) -> Resolution:
    local_eid = int(snapshot["local_eid"])
    remote_eid = int(snapshot["remote_eid"])
    oapp = snapshot["oapp"]

    warnings: list[str] = []
    provenance: list[str] = []

    # 1. Resolve selected receive library.
    app_library = snapshot.get("app_receive_library")
    endpoint_default_library = snapshot.get("endpoint_default_receive_library")

    receive_library = app_library or endpoint_default_library
    if app_library:
        provenance.append("Endpoint receive-library override")
    elif endpoint_default_library:
        provenance.append("Endpoint default receive library")
    else:
        warnings.append("receive-library selection unresolved")

    # 2. Resolve application ULN config if it is actually populated.
    app_uln = snapshot.get("app_uln_config")
    if app_uln and _non_empty(app_uln.get("required_dvns")):
        provenance.append("explicit application ULN config")
        return Resolution(
            status="RESOLVED",
            local_eid=local_eid,
            remote_eid=remote_eid,
            oapp=oapp,
            receive_library=receive_library,
            required_dvns=[_norm_addr(x) for x in app_uln.get("required_dvns", [])],
            optional_dvns=[_norm_addr(x) for x in app_uln.get("optional_dvns", [])],
            optional_threshold=int(app_uln.get("optional_threshold", 0)),
            confirmations=int(app_uln["confirmations"]) if app_uln.get("confirmations") is not None else None,
            executor=_norm_addr((snapshot.get("executor_config") or {}).get("executor")),
            provenance=provenance,
            warnings=warnings,
        )

    # Empty app config is an inheritance signal, not zero-DVN evidence.
    if app_uln is not None:
        provenance.append("application ULN config queried but empty/incomplete")

    lib_defaults = snapshot.get("receive_library_defaults")
    if receive_library and lib_defaults:
        candidate = lib_defaults.get(receive_library.lower())
        if candidate:
            provenance.append("receive-library default ULN config")
            return Resolution(
                status="RESOLVED",
                local_eid=local_eid,
                remote_eid=remote_eid,
                oapp=oapp,
                receive_library=receive_library,
                required_dvns=[_norm_addr(x) for x in candidate.get("required_dvns", [])],
                optional_dvns=[_norm_addr(x) for x in candidate.get("optional_dvns", [])],
                optional_threshold=int(candidate.get("optional_threshold", 0)),
                confirmations=int(candidate["confirmations"]) if candidate.get("confirmations") is not None else None,
                executor=_norm_addr((snapshot.get("executor_config") or {}).get("executor")),
                provenance=provenance,
                warnings=warnings,
            )

    historical = snapshot.get("historical_resolution")
    if historical:
        provenance.append("historical event reconstruction")
        warnings.append("historical reconstruction supplied by snapshot producer")
        return Resolution(
            status="RESOLVED",
            local_eid=local_eid,
            remote_eid=remote_eid,
            oapp=oapp,
            receive_library=receive_library,
            required_dvns=[_norm_addr(x) for x in historical.get("required_dvns", [])],
            optional_dvns=[_norm_addr(x) for x in historical.get("optional_dvns", [])],
            optional_threshold=int(historical.get("optional_threshold", 0)),
            confirmations=int(historical["confirmations"]) if historical.get("confirmations") is not None else None,
            executor=_norm_addr((snapshot.get("executor_config") or {}).get("executor")),
            provenance=provenance,
            warnings=warnings,
        )

    warnings.append("effective receive configuration could not be reconstructed")
    return Resolution(
        status="UNRESOLVED",
        local_eid=local_eid,
        remote_eid=remote_eid,
        oapp=oapp,
        receive_library=receive_library,
        required_dvns=[],
        optional_dvns=[],
        optional_threshold=0,
        confirmations=None,
        executor=_norm_addr((snapshot.get("executor_config") or {}).get("executor")),
        provenance=provenance,
        warnings=warnings,
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: layerzero_effective_config.py snapshot.json", file=sys.stderr)
        return 2
    with open(sys.argv[1], "r", encoding="utf-8") as fh:
        snapshot = json.load(fh)
    result = resolve(snapshot)
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0 if result.status in {"RESOLVED", "UNRESOLVED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
