#!/usr/bin/env python3
"""Resolve effective LayerZero V2 receive ULN configuration from a deterministic snapshot.

RPC/event acquisition is intentionally separate. This resolver models the semantics
of MessageLibManager + UlnBase:

- receive-library selection: OApp override -> Endpoint default;
- receive ULN fields: OApp values selectively override the library default;
- required/optional DVN count 0 means DEFAULT;
- required/optional DVN count 255 means NONE;
- confirmations 0 means DEFAULT;
- confirmations uint64.max means literal zero;
- the final effective ULN configuration must contain at least one DVN.

Executor configuration is retained only as send-side context and is never used
to resolve the receive-side ULN quorum.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from typing import Any

DEFAULT = 0
NIL_DVN_COUNT = 255
NIL_CONFIRMATIONS = 2**64 - 1


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


def _count(config: dict[str, Any], field: str, list_field: str) -> int:
    if field in config and config[field] is not None:
        return int(config[field])
    return len(config.get(list_field, []))


def _validate_explicit_list(config: dict[str, Any], count: int, list_field: str) -> bool:
    values = config.get(list_field, [])
    if count in (DEFAULT, NIL_DVN_COUNT):
        return not values
    return len(values) == count


def _merge_uln(
    app: dict[str, Any] | None,
    default: dict[str, Any] | None,
    provenance: list[str],
) -> tuple[dict[str, Any] | None, list[str]]:
    if default is None:
        return None, ["receive-library default ULN config unavailable"]

    app = app or {}
    warnings: list[str] = []

    required_count = _count(app, "required_dvn_count", "required_dvns")
    optional_count = _count(app, "optional_dvn_count", "optional_dvns")

    if not _validate_explicit_list(app, required_count, "required_dvns"):
        return None, ["application required DVN list/count is inconsistent"]
    if not _validate_explicit_list(app, optional_count, "optional_dvns"):
        return None, ["application optional DVN list/count is inconsistent"]

    default_required = [
        _norm_addr(x) for x in default.get("required_dvns", [])
    ]
    default_optional = [
        _norm_addr(x) for x in default.get("optional_dvns", [])
    ]
    default_optional_threshold = int(default.get("optional_threshold", 0))
    default_confirmations = int(default.get("confirmations", 0))

    # UlnBase semantics: 0 means inherit; 255 means literal NONE.
    if required_count == DEFAULT:
        required_dvns = default_required
    elif required_count == NIL_DVN_COUNT:
        required_dvns = []
    else:
        required_dvns = [_norm_addr(x) for x in app.get("required_dvns", [])]

    if optional_count == DEFAULT:
        optional_dvns = default_optional
        optional_threshold = default_optional_threshold
    elif optional_count == NIL_DVN_COUNT:
        optional_dvns = []
        optional_threshold = 0
    else:
        optional_dvns = [_norm_addr(x) for x in app.get("optional_dvns", [])]
        optional_threshold = int(app.get("optional_threshold", 0))

    app_confirmations = int(app.get("confirmations", DEFAULT))
    if app_confirmations == DEFAULT:
        confirmations = default_confirmations
    elif app_confirmations == NIL_CONFIRMATIONS:
        confirmations = 0
    else:
        confirmations = app_confirmations

    effective = {
        "required_dvns": required_dvns,
        "optional_dvns": optional_dvns,
        "optional_threshold": optional_threshold,
        "confirmations": confirmations,
    }

    if not required_dvns and optional_threshold == 0:
        warnings.append(
            "effective receive ULN config has no DVN quorum; deployed UlnBase would reject it"
        )
        return effective, warnings

    provenance.append("receive ULN resolved with field-level inheritance semantics")
    return effective, warnings


def _resolution(
    *,
    status: str,
    local_eid: int,
    remote_eid: int,
    oapp: str,
    receive_library: str | None,
    effective: dict[str, Any] | None,
    executor: str | None,
    provenance: list[str],
    warnings: list[str],
) -> Resolution:
    return Resolution(
        status=status,
        local_eid=local_eid,
        remote_eid=remote_eid,
        oapp=oapp,
        receive_library=receive_library,
        required_dvns=(effective or {}).get("required_dvns", []),
        optional_dvns=(effective or {}).get("optional_dvns", []),
        optional_threshold=int((effective or {}).get("optional_threshold", 0)),
        confirmations=(
            int((effective or {})["confirmations"])
            if effective is not None and effective.get("confirmations") is not None
            else None
        ),
        executor=executor,
        provenance=provenance,
        warnings=warnings,
    )


def resolve(snapshot: dict[str, Any]) -> Resolution:
    local_eid = int(snapshot["local_eid"])
    remote_eid = int(snapshot["remote_eid"])
    oapp = snapshot["oapp"]

    warnings: list[str] = []
    provenance: list[str] = []

    # 1. Resolve the effective receive library.
    app_library = snapshot.get("app_receive_library")
    endpoint_default_library = snapshot.get("endpoint_default_receive_library")
    receive_library = app_library or endpoint_default_library

    if app_library:
        provenance.append("Endpoint receive-library override")
    elif endpoint_default_library:
        provenance.append("Endpoint default receive library")
    else:
        warnings.append("receive-library selection unresolved")

    executor = _norm_addr((snapshot.get("executor_config") or {}).get("executor"))
    if snapshot.get("executor_config") is not None:
        warnings.append(
            "executor configuration is send-side context and is not used for receive ULN resolution"
        )

    # 2. Resolve receive ULN through field-level inheritance.
    app_uln = snapshot.get("app_uln_config")
    lib_defaults = snapshot.get("receive_library_defaults") or {}
    default_uln = (
        lib_defaults.get(receive_library.lower())
        if receive_library
        else None
    )

    if app_uln is not None:
        provenance.append("application ULN config observed")
        effective, merge_warnings = _merge_uln(app_uln, default_uln, provenance)
        warnings.extend(merge_warnings)
        if effective is not None:
            status = "RESOLVED" if not merge_warnings or all(
                "would reject" not in w for w in merge_warnings
            ) else "UNRESOLVED"
            return _resolution(
                status=status,
                local_eid=local_eid,
                remote_eid=remote_eid,
                oapp=oapp,
                receive_library=receive_library,
                effective=effective,
                executor=executor,
                provenance=provenance,
                warnings=warnings,
            )

    # 3. Optional historical reconstruction may supply the final effective state.
    historical = snapshot.get("historical_resolution")
    if historical:
        provenance.append("historical event reconstruction")
        warnings.append("historical reconstruction supplied by snapshot producer")
        return _resolution(
            status="RESOLVED",
            local_eid=local_eid,
            remote_eid=remote_eid,
            oapp=oapp,
            receive_library=receive_library,
            effective={
                "required_dvns": [_norm_addr(x) for x in historical.get("required_dvns", [])],
                "optional_dvns": [_norm_addr(x) for x in historical.get("optional_dvns", [])],
                "optional_threshold": int(historical.get("optional_threshold", 0)),
                "confirmations": (
                    int(historical["confirmations"])
                    if historical.get("confirmations") is not None
                    else None
                ),
            },
            executor=executor,
            provenance=provenance,
            warnings=warnings,
        )

    warnings.append("effective receive configuration could not be reconstructed")
    return _resolution(
        status="UNRESOLVED",
        local_eid=local_eid,
        remote_eid=remote_eid,
        oapp=oapp,
        receive_library=receive_library,
        effective=None,
        executor=executor,
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
