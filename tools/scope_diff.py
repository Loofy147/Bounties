"""Compare normalized, manually reviewed bounty-program scope snapshots."""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
NOT_RECORDED = "NOT_RECORDED"
PROGRAM_META_FIELDS = ("source_url",)
PROGRAM_FIELDS = (
    "reward_ceiling", "reward_currency", "kyc_required", "report_deadline_hours",
    "deadline_rule", "poc_required", "ai_report_policy", "allowed_environments",
    "prohibited_actions", "disclosure_policy", "known_issue_policy",
)
ASSET_FIELDS = (
    "status", "source_url", "eligible_release", "impacts", "max_reward",
    "reward_currency", "allowed_environments", "prohibited_actions", "poc_required",
    "known_issue_policy", "disclosure_policy",
)
VALID_ASSET_STATES = {"in-scope", "out-of-scope", "unknown"}


def _valid_time(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def validate_snapshot(snapshot: Any, label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(snapshot, dict):
        return [f"{label} snapshot must be an object"]
    if snapshot.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}.schema_version must equal {SCHEMA_VERSION!r}")
    program = snapshot.get("program")
    if not isinstance(program, dict):
        errors.append(f"{label}.program must be an object")
        program = {}
    for key in ("id", "name", "source_url"):
        if not isinstance(program.get(key), str) or not program[key].strip():
            errors.append(f"{label}.program.{key} is required")
    if isinstance(program.get("source_url"), str) and not program["source_url"].startswith("https://"):
        errors.append(f"{label}.program.source_url must be HTTPS")
    if not _valid_time(program.get("retrieved_at")):
        errors.append(f"{label}.program.retrieved_at must be ISO-8601 with timezone")
    if not isinstance(program.get("terms"), dict):
        errors.append(f"{label}.program.terms must be an object")
    assets = snapshot.get("assets")
    if not isinstance(assets, list):
        errors.append(f"{label}.assets must be an array")
        assets = []
    seen: set[str] = set()
    for index, asset in enumerate(assets):
        prefix = f"{label}.assets[{index}]"
        if not isinstance(asset, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for key in ("id", "name", "status", "source_url"):
            if not isinstance(asset.get(key), str) or not asset[key].strip():
                errors.append(f"{prefix}.{key} is required")
        asset_id = asset.get("id")
        if isinstance(asset_id, str):
            if asset_id in seen:
                errors.append(f"{label}.assets contains duplicate id {asset_id!r}")
            seen.add(asset_id)
        if asset.get("status") not in VALID_ASSET_STATES:
            errors.append(f"{prefix}.status must be one of: in-scope, out-of-scope, unknown")
        if isinstance(asset.get("source_url"), str) and not asset["source_url"].startswith("https://"):
            errors.append(f"{prefix}.source_url must be HTTPS")
    return errors


def _comparable(value: Any) -> Any:
    if isinstance(value, list) and all(isinstance(item, (str, int, float, bool)) or item is None for item in value):
        return sorted(value, key=lambda item: (type(item).__name__, str(item)))
    return value


def _recorded(mapping: dict[str, Any], key: str) -> Any:
    return mapping[key] if key in mapping else NOT_RECORDED


def diff_snapshots(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    """Return deterministic material differences; timestamps alone do not alert."""
    errors = validate_snapshot(old, "old") + validate_snapshot(new, "new")
    if errors:
        raise ValueError("; ".join(errors))
    old_program, new_program = old["program"], new["program"]
    if old_program["id"] != new_program["id"]:
        raise ValueError("cannot compare snapshots from different program ids")
    deltas: list[dict[str, Any]] = []

    def compare_fields(before: dict[str, Any], after: dict[str, Any], fields: tuple[str, ...], prefix: str, kind: str) -> None:
        for field in fields:
            if field not in before and field not in after:
                continue
            old_value, new_value = _recorded(before, field), _recorded(after, field)
            if _comparable(old_value) == _comparable(new_value):
                continue
            deltas.append({
                "kind": kind, "path": f"{prefix}.{field}",
                "before": old_value, "after": new_value, "material": True,
            })

    compare_fields(old_program, new_program, PROGRAM_META_FIELDS, "program", "program_metadata_changed")
    compare_fields(old_program.get("terms", {}), new_program.get("terms", {}), PROGRAM_FIELDS, "terms", "program_term_changed")
    old_assets = {asset["id"]: asset for asset in old["assets"]}
    new_assets = {asset["id"]: asset for asset in new["assets"]}
    for asset_id in sorted(new_assets.keys() - old_assets.keys()):
        deltas.append({"kind": "asset_added", "path": f"assets[{asset_id}]", "before": None,
                       "after": new_assets[asset_id], "material": True})
    for asset_id in sorted(old_assets.keys() - new_assets.keys()):
        deltas.append({"kind": "asset_removed", "path": f"assets[{asset_id}]",
                       "before": old_assets[asset_id], "after": None, "material": True})
    for asset_id in sorted(old_assets.keys() & new_assets.keys()):
        compare_fields(old_assets[asset_id], new_assets[asset_id], ASSET_FIELDS, f"assets[{asset_id}]", "asset_field_changed")
    deltas.sort(key=lambda delta: (delta["path"], delta["kind"]))
    return {
        "schema_version": SCHEMA_VERSION,
        "program_id": old_program["id"],
        "old_retrieved_at": old_program["retrieved_at"],
        "new_retrieved_at": new_program["retrieved_at"],
        "changed": bool(deltas),
        "deltas": deltas,
        "disclaimer": "This is a structural diff of normalized snapshots, not an independent determination of bounty eligibility or vulnerability.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diff two normalized, reviewed bounty scope snapshots.")
    parser.add_argument("old", type=Path, help="Previous JSON snapshot")
    parser.add_argument("new", type=Path, help="Current JSON snapshot")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args(argv)
    try:
        old = json.loads(args.old.read_text(encoding="utf-8"))
        new = json.loads(args.new.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    try:
        result = diff_snapshots(old, new)
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
