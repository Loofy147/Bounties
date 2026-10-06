#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
from validate_layerzero_snapshot import validate

DATA = Path(__file__).resolve().parent / "data"

def load(name):
    return json.loads((DATA / name).read_text())

def main():
    template = load("iota_lockbox_snapshot_template.json")
    errors = validate(template)
    assert errors, "unpopulated template must fail closed"

    valid = template.copy()
    valid["block"] = {
        "number": 100,
        "hash": "0x" + "11" * 32,
        "rpc_provenance": "LOCAL_FORK_TEST"
    }
    valid["code_identity"] = {
        "proxy": "0x" + "22" * 20,
        "implementation": "0x" + "33" * 20,
        "runtime_match": "exact_match"
    }
    valid["endpoint"] = {
        "address": "0x1a44076050125825900e736c501f859c50fE728c"
    }
    valid["receive_path"] = {
        "app_receive_library": "0x" + "44" * 20,
        "default_receive_library": "0x" + "55" * 20,
        "effective_receive_library": "0x" + "44" * 20,
        "is_default": False,
        "timeout": {"library": None, "expiry_block": None}
    }
    valid["peer"] = {
        "remote_eid": 30423,
        "value": "0x" + "66" * 32
    }
    valid["receive_uln"] = {
        "status": "RESOLVED",
        "required_dvns": ["0x" + "77" * 20, "0x" + "88" * 20],
        "optional_dvns": [],
        "optional_threshold": 0,
        "confirmations": 20,
        "resolution_provenance": ["local-fork eth_call", "ReceiveUln302:getUlnConfig"]
    }
    valid["provenance"] = {
        "rpc": "LOCAL_FORK_TEST",
        "source_revision": "LayerZero-v2/main:c656547812047d3db46987a161930cc3525eb69e"
    }
    assert not validate(valid)

    grace = json.loads(json.dumps(valid))
    grace["block"]["number"] = 120
    grace["receive_path"]["effective_receive_library"] = "0x" + "55" * 20
    grace["receive_path"]["timeout"] = {
        "library": "0x" + "44" * 20,
        "expiry_block": 121
    }
    grace["receive_path"]["is_default"] = False
    assert not validate(grace)
    assert grace["receive_path"]["grace_active"] is True

    print("PASS unpopulated snapshot fails closed")
    print("PASS resolved local-fork snapshot validates")
    print("PASS active receive-library grace period is represented")
    print("RESULT LayerZeroSnapshotValidator = PASS")

if __name__ == "__main__":
    main()
