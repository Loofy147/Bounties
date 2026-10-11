#!/usr/bin/env python3
"""Fail-closed validator for an authorized local-fork LayerZero V2 snapshot.

This tool does not access Ethereum or any external RPC. It validates the evidence
bundle produced by a separate, explicitly authorized local-fork acquisition step.

The validator deliberately distinguishes:
- documented policy from observed state;
- current receive library from grace-period acceptance;
- receive-side ULN from send-side Executor configuration;
- UNKNOWN from numeric zero.

It never upgrades an unknown field to a default value.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ZERO = "0x" + "00" * 32
ZERO_ADDR = "0x" + "00" * 20


class ValidationError(Exception):
    pass


def req(obj: dict[str, Any], key: str, context: str = "") -> Any:
    if key not in obj:
        raise ValidationError(f"missing {context + '.' if context else ''}{key}")
    return obj[key]


def addr(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 42 or not value.startswith("0x"):
        raise ValidationError(f"{field}: expected 20-byte hex address")
    int(value[2:], 16)
    return value.lower()


def b32(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 66 or not value.startswith("0x"):
        raise ValidationError(f"{field}: expected bytes32 hex")
    int(value[2:], 16)
    return value.lower()


def nonnegative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValidationError(f"{field}: expected non-negative integer")
    return value


def validate(snapshot: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    try:
        target = req(snapshot, "target")
        block = req(snapshot, "block")
        code = req(snapshot, "code_identity")
        endpoint = req(snapshot, "endpoint")
        receive = req(snapshot, "receive_path")
        peer = req(snapshot, "peer")
        uln = req(snapshot, "receive_uln")
        provenance = req(snapshot, "provenance")

        if req(snapshot, "schema_version") != "layerzero-local-fork-snapshot/v0.1":
            raise ValidationError("unsupported schema_version")

        if req(target, "chain_id") != 1:
            raise ValidationError("target.chain_id must be Ethereum mainnet chain id 1")
        if req(target, "local_eid") != 30101:
            raise ValidationError("target.local_eid must be 30101")
        if req(target, "remote_eid") != 30423:
            raise ValidationError("target.remote_eid must be IOTA EID 30423")

        addr(req(target, "oapp"), "target.oapp")
        nonnegative_int(req(block, "number"), "block.number")
        b32(req(block, "hash"), "block.hash")
        if not req(block, "rpc_provenance"):
            raise ValidationError("block.rpc_provenance is required")

        addr(req(code, "proxy"), "code_identity.proxy")
        addr(req(code, "implementation"), "code_identity.implementation")
        if req(code, "runtime_match") not in {"exact_match", "UNKNOWN"}:
            raise ValidationError("code_identity.runtime_match must be exact_match or UNKNOWN")
        addr(req(endpoint, "address"), "endpoint.address")

        # Receive-library selection and grace period are coupled.
        app_lib = req(receive, "app_receive_library")
        default_lib = req(receive, "default_receive_library")
        effective_lib = req(receive, "effective_receive_library")
        is_default = req(receive, "is_default")
        timeout = req(receive, "timeout")

        for name, value in (
            ("receive_path.app_receive_library", app_lib),
            ("receive_path.default_receive_library", default_lib),
            ("receive_path.effective_receive_library", effective_lib),
        ):
            if value is not None:
                addr(value, name)

        if not isinstance(is_default, bool):
            raise ValidationError("receive_path.is_default must be boolean")

        old_lib = timeout.get("library")
        expiry = timeout.get("expiry_block")
        if old_lib is not None:
            addr(old_lib, "receive_path.timeout.library")
        if expiry is not None:
            nonnegative_int(expiry, "receive_path.timeout.expiry_block")

        block_number = block["number"]
        if is_default:
            if app_lib not in (None, ZERO_ADDR):
                raise ValidationError("is_default=true but app_receive_library is not default/zero")
        else:
            if app_lib in (None, ZERO_ADDR):
                raise ValidationError("is_default=false but app_receive_library is unset/zero")

        if effective_lib in (None, ZERO_ADDR):
            raise ValidationError("effective_receive_library must be resolved before snapshot release")

        grace_active = (
            old_lib not in (None, ZERO_ADDR)
            and isinstance(expiry, int)
            and expiry > block_number
            and old_lib.lower() != effective_lib.lower()
        )
        receive["grace_active"] = grace_active

        # Peer: zero is meaningful, not a missing-value substitute.
        peer_value = b32(req(peer, "value"), "peer.value")
        peer["is_zero"] = peer_value == ZERO
        peer["remote_eid"] = nonnegative_int(req(peer, "remote_eid"), "peer.remote_eid")
        if peer["remote_eid"] != 30423:
            raise ValidationError("peer.remote_eid must be 30423")

        # Receive ULN must be explicit enough to explain effective quorum.
        status = req(uln, "status")
        if status not in {"RESOLVED", "UNRESOLVED", "CONFLICTED"}:
            raise ValidationError("receive_uln.status invalid")

        if status == "RESOLVED":
            for field in ("required_dvns", "optional_dvns"):
                values = req(uln, field)
                if not isinstance(values, list):
                    raise ValidationError(f"receive_uln.{field} must be a list")
                for i, value in enumerate(values):
                    addr(value, f"receive_uln.{field}[{i}]")
            threshold = nonnegative_int(req(uln, "optional_threshold"), "receive_uln.optional_threshold")
            required = uln["required_dvns"]
            optional = uln["optional_dvns"]
            if not required and threshold == 0:
                raise ValidationError("RESOLVED receive ULN has no DVN quorum")
            if threshold > len(optional):
                raise ValidationError("optional_threshold exceeds optional_dvns length")
            nonnegative_int(req(uln, "confirmations"), "receive_uln.confirmations")
            if not req(uln, "resolution_provenance"):
                raise ValidationError("resolved receive ULN requires provenance")

        # Executor is explicitly non-authoritative for receive quorum.
        send = snapshot.get("send_context")
        if send is not None:
            if send.get("executor") is not None:
                addr(send["executor"], "send_context.executor")
            if send.get("max_message_size") is not None:
                nonnegative_int(send["max_message_size"], "send_context.max_message_size")

        required_provenance = ("rpc", "source_revision")
        for field in required_provenance:
            if not provenance.get(field):
                raise ValidationError(f"provenance.{field} is required")

    except (ValidationError, TypeError, KeyError, ValueError) as exc:
        errors.append(str(exc))

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_layerzero_snapshot.py snapshot.json", file=sys.stderr)
        return 2

    snapshot_path = Path(sys.argv[1])
    try:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID INPUT: {exc}", file=sys.stderr)
        return 2

    errors = validate(snapshot)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        print("RESULT LayerZeroLocalForkSnapshot = REJECTED")
        return 1

    print("PASS target identity")
    print("PASS block-pinned provenance")
    print("PASS implementation/endpoint identity fields")
    print("PASS receive-library + grace-period consistency")
    print("PASS peer identity field")
    print("PASS receive-side ULN evidence gate")
    print("PASS send-side Executor kept separate")
    print("RESULT LayerZeroLocalForkSnapshot = ACCEPTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
