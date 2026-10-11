#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
from layerzero_effective_config import resolve

DATA = Path(__file__).resolve().parent / "data"

def load(name):
    return json.loads((DATA / name).read_text())

def main():
    explicit = resolve(load("layerzero_config_explicit.json"))
    assert explicit.status == "RESOLVED"
    assert explicit.required_dvns == ["0xdvn-a"]
    assert explicit.optional_dvns == ["0xdvn-b"]
    assert explicit.optional_threshold == 1
    assert explicit.confirmations == 20
    assert "receive ULN resolved with field-level inheritance semantics" in explicit.provenance

    inherited = resolve(load("layerzero_config_inherited.json"))
    assert inherited.status == "RESOLVED"
    assert inherited.required_dvns == ["0xdvn-default"]
    assert inherited.optional_dvns == []
    assert inherited.confirmations == 15
    assert "receive ULN resolved with field-level inheritance semantics" in inherited.provenance

    explicit_no_default = resolve(load("layerzero_config_explicit_no_default.json"))
    assert explicit_no_default.status == "RESOLVED"
    assert explicit_no_default.required_dvns == ["0xdvn-a"]
    assert explicit_no_default.confirmations == 20

    partial = resolve(load("layerzero_config_partial_override.json"))
    assert partial.status == "RESOLVED"
    assert partial.required_dvns == ["0xdvn-default"]
    assert partial.optional_dvns == ["0xdvn-custom-a", "0xdvn-custom-b"]
    assert partial.optional_threshold == 1
    assert partial.confirmations == 15

    unresolved = resolve(load("layerzero_config_unresolved.json"))
    assert unresolved.status == "UNRESOLVED"
    assert "effective receive configuration could not be reconstructed" in unresolved.warnings

    invalid = resolve(load("layerzero_config_invalid_no_dvn.json"))
    assert invalid.status == "UNRESOLVED"
    assert any("would reject" in warning for warning in invalid.warnings)

    print("PASS explicit application configuration")
    print("PASS inherited default configuration")
    print("PASS fully explicit configuration does not require defaults")
    print("PASS partial field-level override")
    print("PASS unresolved configuration remains UNRESOLVED")
    print("PASS zero-DVN result is rejected by modeled UlnBase invariant")
    print("RESULT LayerZeroEffectiveConfigResolver = PASS")

if __name__ == "__main__":
    main()
