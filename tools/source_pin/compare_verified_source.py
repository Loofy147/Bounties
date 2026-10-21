#!/usr/bin/env python3
"""Fail-closed comparison of a verified Solidity source unit to a pinned repo file.

The tool is intentionally offline. It never downloads targets, executes contracts, or
makes an eligibility decision. Comment/whitespace-normalized equality is diagnostic
only and does not count as an exact source pin.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def solidity_lexical_form(source: str) -> str:
    """Normalize comments and external whitespace without changing string literals.

    This is a triage fingerprint, not a Solidity parser or proof of semantic
    equivalence. It preserves a separator where a comment/whitespace occurred so
    adjacent tokens cannot silently concatenate (for example, the token sequence
    "uint a" vs "uinta").
    """
    out: list[str] = []
    i = 0
    n = len(source)
    pending_space = False

    def emit_space() -> None:
        nonlocal pending_space
        if out and out[-1] != " ":
            pending_space = True

    def emit_char(ch: str) -> None:
        nonlocal pending_space
        if pending_space and out and out[-1] != " ":
            out.append(" ")
        pending_space = False
        out.append(ch)

    while i < n:
        ch = source[i]
        nxt = source[i + 1] if i + 1 < n else ""

        if ch.isspace():
            emit_space()
            i += 1
            continue

        if ch == "/" and nxt == "/":
            emit_space()
            i += 2
            while i < n and source[i] not in "\r\n":
                i += 1
            continue

        if ch == "/" and nxt == "*":
            emit_space()
            i += 2
            end = source.find("*/", i)
            if end < 0:
                raise ValueError("unterminated Solidity block comment")
            i = end + 2
            continue

        if ch in ("'", '"'):
            # Preserve string/character literal bytes exactly, including spaces and
            # comment-looking sequences. Backslash escapes consume the next byte.
            emit_char(ch)
            quote = ch
            i += 1
            closed = False
            while i < n:
                cur = source[i]
                emit_char(cur)
                if cur == "\\":
                    i += 1
                    if i < n:
                        emit_char(source[i])
                        i += 1
                    continue
                if cur == quote:
                    i += 1
                    closed = True
                    break
                i += 1
            if not closed:
                raise ValueError("unterminated Solidity string/character literal")
            continue

        emit_char(ch)
        i += 1

    return "".join(out).strip()


def unified_diff_excerpt(left: str, right: str, max_lines: int = 24) -> list[str]:
    diff = list(
        difflib.unified_diff(
            left.splitlines(),
            right.splitlines(),
            fromfile="verified-source",
            tofile="repository-source",
            lineterm="",
        )
    )
    return diff[:max_lines]


def load_verified_source(metadata_path: Path, source_unit: str) -> tuple[str, dict[str, Any]]:
    try:
        document = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read verified-source JSON: {exc}") from exc

    sources = document.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("verified-source JSON has no 'sources' object")
    entry = sources.get(source_unit)
    if isinstance(entry, dict):
        verified_source = entry.get("content")
    elif isinstance(entry, str):
        verified_source = entry
    else:
        verified_source = None
    if not isinstance(verified_source, str):
        raise ValueError(f"source unit {source_unit!r} has no embedded 'content'")

    compiler = document.get("metadata", {}).get("compiler", {})
    settings = document.get("metadata", {}).get("settings", {})
    summary: dict[str, Any] = {
        "address": document.get("address"),
        "chain_id": document.get("chainId"),
        "verification_match": document.get("match"),
        "verified_at": document.get("verifiedAt"),
        "compiler_version": compiler.get("version"),
        "optimizer": settings.get("optimizer"),
        "evm_version": settings.get("evmVersion"),
    }
    return verified_source, summary


def compare_sources(verified_source: str, repo_source: str) -> dict[str, Any]:
    verified_lexical = solidity_lexical_form(verified_source)
    repo_lexical = solidity_lexical_form(repo_source)
    text_match = verified_source == repo_source
    lexical_match = verified_lexical == repo_lexical
    if text_match:
        status = "EXACT_TEXT_MATCH"
    elif lexical_match:
        status = "COMMENT_OR_WHITESPACE_ONLY_DIFF"
    else:
        status = "SOURCE_CONTENT_MISMATCH"

    return {
        "status": status,
        "exact_text_match": text_match,
        "comment_whitespace_normalized_match": lexical_match,
        "verified_source_bytes": len(verified_source.encode("utf-8")),
        "repository_source_bytes": len(repo_source.encode("utf-8")),
        "verified_source_sha256": sha256_text(verified_source),
        "repository_source_sha256": sha256_text(repo_source),
        "verified_normalized_sha256": sha256_text(verified_lexical),
        "repository_normalized_sha256": sha256_text(repo_lexical),
        "diff_excerpt": [] if text_match else unified_diff_excerpt(verified_source, repo_source),
        "gate_note": (
            "Exact source-text equality observed. Still verify address, chain, block, compiler settings, "
            "immutables/constructor arguments and the program's eligible-target terms."
            if text_match
            else "FAIL CLOSED: normalized equality is only diagnostic; it is not an exact source pin, "
            "bytecode reproduction, or bounty-eligibility decision. Human review is required."
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verified-json", required=True, type=Path, help="Local Sourcify API v2 JSON response")
    parser.add_argument("--source-unit", required=True, help="Exact path key from JSON sources, e.g. src/transit/TransitStation.sol")
    parser.add_argument("--repo-file", required=True, type=Path, help="Pinned repository source file")
    parser.add_argument("--output", type=Path, help="Optional path to write the JSON evidence record")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        verified_source, metadata = load_verified_source(args.verified_json, args.source_unit)
        repo_source = args.repo_file.read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "INPUT_ERROR", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2

    result: dict[str, Any] = {
        "source_unit": args.source_unit,
        "verified_json_path": str(args.verified_json),
        "repository_file": str(args.repo_file),
        "metadata": metadata,
        **compare_sources(verified_source, repo_source),
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        try:
            args.output.write_text(rendered + "\n", encoding="utf-8")
        except OSError as exc:
            print(json.dumps({"status": "OUTPUT_ERROR", "error": str(exc)}, indent=2), file=sys.stderr)
            return 2
    print(rendered)
    # Strict mode: every non-exact source string is a non-zero exit, even if only
    # comments or whitespace differ. A researcher may inspect the normalized result,
    # but the utility never silently promotes it to an exact pin.
    if result["status"] == "EXACT_TEXT_MATCH":
        return 0
    if result["status"] == "COMMENT_OR_WHITESPACE_ONLY_DIFF":
        return 1
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
