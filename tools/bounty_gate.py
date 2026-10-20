"""Fail-closed validation for evidence-driven bounty research records."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
STATUSES = ("RECONNAISSANCE", "HYPOTHESIS", "REPRODUCED", "IN-SCOPE", "SUBMITTED", "ACCEPTED", "PAID", "REJECTED")
_EVIDENCE_REQUIRED = {"REPRODUCED", "IN-SCOPE", "SUBMITTED", "ACCEPTED", "PAID"}
_COMMIT_RE = re.compile(r"^(?:[0-9a-fA-F]{7,40}|[0-9a-fA-F]{64})$")
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_REQUIRED_GATES = (
    "scope_reviewed", "release_pinned", "known_issues_reviewed", "audits_reviewed",
    "impact_mapped_to_program", "independent_review_passed", "human_approved",
    "submission_human_authored", "deadline_checked", "eligibility_confirmed",
)


def _parse_time(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be an ISO-8601 timestamp with timezone")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be a valid ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        errors.append(f"{label} must include a timezone")
        return None
    return parsed.astimezone(timezone.utc)


def _is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def _mapping(record: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = record.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key} must be an object")
        return {}
    return value


def validate_record(record: dict[str, Any], *, root: Path, now: str | None = None) -> dict[str, Any]:
    """Validate record completeness and policy gates; never promote a claim."""
    errors: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "submission_gate_pass": False, "claim_status": None,
                "errors": ["record must be a JSON object"], "warnings": [],
                "blocking_gates": ["valid_record"]}

    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION!r}")
    target = _mapping(record, "target", errors)
    claim = _mapping(record, "claim", errors)
    experiment = _mapping(record, "experiment", errors)
    gates = _mapping(record, "gates", errors)
    terms = _mapping(record, "program_terms", errors)
    evidence = record.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence must be an array")
        evidence = []

    for key in ("program", "asset", "source_url", "repository"):
        if not isinstance(target.get(key), str) or not target[key].strip():
            errors.append(f"target.{key} is required")
    if not isinstance(target.get("source_url"), str) or not str(target.get("source_url", "")).startswith("https://"):
        errors.append("target.source_url must be an HTTPS URL")
    revision = target.get("revision")
    if not isinstance(revision, str) or not _COMMIT_RE.fullmatch(revision):
        errors.append("target.revision must be an immutable commit/hash, not a branch or moving ref")
    for key in ("eligible_release_confirmed", "in_scope"):
        if not _is_bool(target.get(key)):
            errors.append(f"target.{key} must be a boolean")
    if target.get("in_scope") is not True:
        errors.append("target is not confirmed within the current program scope")
    if target.get("eligible_release_confirmed") is not True:
        blockers.append("target.eligible_release_confirmed")
    scope_checked = _parse_time(target.get("scope_snapshot_checked_at"), "target.scope_snapshot_checked_at", errors)

    allowed_envs = target.get("allowed_environments")
    if not isinstance(allowed_envs, list) or not allowed_envs or any(not isinstance(x, str) or not x for x in allowed_envs):
        errors.append("target.allowed_environments must be a non-empty array of environment names")
        allowed_envs = []
    prohibited_actions = target.get("prohibited_actions", [])
    allowed_actions = target.get("allowed_actions", [])
    if not isinstance(prohibited_actions, list) or any(not isinstance(x, str) for x in prohibited_actions):
        errors.append("target.prohibited_actions must be an array of strings")
        prohibited_actions = []
    if not isinstance(allowed_actions, list) or any(not isinstance(x, str) for x in allowed_actions):
        errors.append("target.allowed_actions must be an array of strings")
        allowed_actions = []
    prohibited_norm = {x.strip().lower().replace("_", "-") for x in prohibited_actions}
    allowed_norm = {x.strip().lower().replace("_", "-") for x in allowed_actions}

    env = experiment.get("environment")
    if not isinstance(env, str) or env not in allowed_envs:
        errors.append("experiment.environment is not in target.allowed_environments")
    for key in ("target_matches_scope", "destructive", "uses_public_network", "reproducible", "poc_passed"):
        if not _is_bool(experiment.get(key)):
            errors.append(f"experiment.{key} must be a boolean")
    if experiment.get("target_matches_scope") is not True:
        errors.append("experiment target is not confirmed within the current program scope")
    if experiment.get("uses_public_network") is True:
        if "public-network-testing" in prohibited_norm or "public-network-testing" not in allowed_norm:
            errors.append("experiment uses a public network without explicit program authorization")
    if experiment.get("destructive") is True:
        if "destructive-testing" in prohibited_norm or "destructive-testing" not in allowed_norm:
            errors.append("experiment is destructive but destructive testing is not explicitly authorized")
    if "denial-of-service" in prohibited_norm and experiment.get("denial_of_service") is True:
        errors.append("denial-of-service activity is prohibited by the current target contract")
    if "third-party-contract-testing" in prohibited_norm and experiment.get("tests_third_party_contracts") is True:
        errors.append("third-party contract testing is prohibited by the current target contract")

    status = claim.get("status")
    if status not in STATUSES:
        errors.append("claim.status must be one of: " + ", ".join(STATUSES))
        status = None
    for key in ("id", "title", "hypothesis", "claimed_impact"):
        if not isinstance(claim.get(key), str) or not claim[key].strip():
            errors.append(f"claim.{key} is required")
    first_discovered = _parse_time(claim.get("first_discovered_at"), "claim.first_discovered_at", errors)
    if status in _EVIDENCE_REQUIRED and not evidence:
        errors.append(f"claim status {status} or later requires at least one evidence item")

    workspace = root.resolve()
    for index, item in enumerate(evidence):
        prefix = f"evidence[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for key in ("id", "kind"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(f"{prefix}.{key} is required")
        if revision and item.get("target_revision") != revision:
            errors.append(f"{prefix}.target_revision does not match target.revision")
        _parse_time(item.get("observed_at"), f"{prefix}.observed_at", errors)
        if not _is_bool(item.get("reproducible")):
            errors.append(f"{prefix}.reproducible must be a boolean")
        rel_path, digest, evidence_url = item.get("path"), item.get("sha256"), item.get("url")
        if rel_path is None and evidence_url is None:
            errors.append(f"{prefix} requires either a local path or an HTTPS evidence URL")
        if evidence_url is not None and (not isinstance(evidence_url, str) or not evidence_url.startswith("https://")):
            errors.append(f"{prefix}.url must be an HTTPS URL")
        if rel_path is not None:
            if not isinstance(rel_path, str) or not rel_path.strip():
                errors.append(f"{prefix}.path must be a non-empty relative path or null")
            else:
                artifact = (workspace / rel_path).resolve()
                if artifact != workspace and workspace not in artifact.parents:
                    errors.append(f"{prefix}.path escapes repository root")
                elif not artifact.is_file():
                    errors.append(f"{prefix}.path does not resolve to an existing evidence file")
                elif digest is not None:
                    if not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
                        errors.append(f"{prefix}.sha256 must be a 64-character SHA-256 hex digest")
                    elif hashlib.sha256(artifact.read_bytes()).hexdigest().lower() != digest.lower():
                        errors.append(f"{prefix}.sha256 does not match the evidence file")
                else:
                    warnings.append(f"{prefix}.sha256 is missing; artifact integrity is not verified")
        elif digest is not None:
            errors.append(f"{prefix}.sha256 cannot be verified without evidence[{index}].path")
        elif evidence_url is not None:
            warnings.append(f"{prefix}.url is a provenance pointer; remote content and integrity were not fetched")

    for key in _REQUIRED_GATES:
        if gates.get(key) is not True:
            blockers.append(f"gates.{key}")
    ai_policy = terms.get("ai_report_policy")
    if ai_policy not in {"allowed", "prohibited", "unknown"}:
        errors.append("program_terms.ai_report_policy must be 'allowed', 'prohibited', or 'unknown'")
    if not _is_bool(gates.get("ai_generated_report")):
        errors.append("gates.ai_generated_report must be a boolean")
    elif ai_policy == "prohibited" and gates.get("ai_generated_report") is True:
        errors.append("AI-generated external reports are prohibited by the current program terms")
    elif ai_policy == "unknown":
        blockers.append("program_terms.ai_report_policy")
    if gates.get("submission_human_authored") is not True:
        blockers.append("gates.submission_human_authored")

    if not _is_bool(terms.get("poc_required")):
        errors.append("program_terms.poc_required must be a boolean")
    if not _is_bool(terms.get("deadline_rule_confirmed")):
        errors.append("program_terms.deadline_rule_confirmed must be a boolean")
    deadline_confirmed = terms.get("deadline_rule_confirmed") is True
    if not deadline_confirmed:
        blockers.append("program_terms.deadline_rule_confirmed")
    deadline_hours = terms.get("report_deadline_hours")
    if deadline_hours is not None and (not isinstance(deadline_hours, (int, float)) or isinstance(deadline_hours, bool) or deadline_hours <= 0):
        errors.append("program_terms.report_deadline_hours must be a positive number or null")

    current = _parse_time(now, "now", errors) if now else datetime.now(timezone.utc)
    scope_max_age = terms.get("scope_refresh_max_age_hours")
    if scope_max_age is None:
        blockers.append("program_terms.scope_refresh_max_age_hours")
    elif not isinstance(scope_max_age, (int, float)) or isinstance(scope_max_age, bool) or scope_max_age <= 0:
        errors.append("program_terms.scope_refresh_max_age_hours must be a positive number or null")
    elif scope_checked and current:
        age_hours = (current - scope_checked).total_seconds() / 3600
        if age_hours > float(scope_max_age):
            blockers.append("scope_snapshot_freshness")
        elif age_hours < 0:
            warnings.append("scope snapshot timestamp is in the future relative to validation time")

    if deadline_confirmed and deadline_hours is not None and first_discovered and current:
        elapsed = (current - first_discovered).total_seconds() / 3600
        if elapsed >= float(deadline_hours):
            errors.append("reporting deadline has elapsed since claim.first_discovered_at")
        elif elapsed < 0:
            warnings.append("claim.first_discovered_at is in the future relative to validation time")
    elif deadline_hours is None:
        blockers.append("program_terms.report_deadline_hours")

    if status != "IN-SCOPE":
        blockers.append("claim.status must be explicitly reviewed as IN-SCOPE")
    if experiment.get("reproducible") is not True:
        blockers.append("experiment.reproducible")
    if terms.get("poc_required") is True and experiment.get("poc_passed") is not True:
        blockers.append("experiment.poc_passed")
    if target.get("eligible_release_confirmed") is not True:
        blockers.append("target.eligible_release_confirmed")

    errors = list(dict.fromkeys(errors))
    warnings = list(dict.fromkeys(warnings))
    blockers = list(dict.fromkeys(blockers))
    valid = not errors
    return {
        "valid": valid,
        "submission_gate_pass": valid and not blockers,
        "claim_status": status,
        "errors": errors,
        "warnings": warnings,
        "blocking_gates": blockers,
        "disclaimer": "A passing gate is not a vulnerability finding, scope acceptance, severity rating, or guarantee of reward. Human review and the program's final decision remain required.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an evidence-driven bounty research JSON record.")
    parser.add_argument("record", type=Path, help="Path to a research record JSON file")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository/workspace root for evidence paths")
    parser.add_argument("--now", help="Override current time (ISO-8601 with timezone), for deterministic checks")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--require-submission-gate", action="store_true", help="Return exit code 3 when valid but submission gates remain blocked")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    result = validate_record(data, root=args.root, now=args.now)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    if not result["valid"]:
        return 1
    if args.require_submission_gate and not result["submission_gate_pass"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
