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
    assert "explicit application ULN config" in explicit.provenance

    inherited = resolve(load("layerzero_config_inherited.json"))
    assert inherited.status == "RESOLVED"
    assert inherited.required_dvns == ["0xdvn-default"]
    assert "application ULN config queried but empty/incomplete" in inherited.provenance
    assert "receive-library default ULN config" in inherited.provenance

    unresolved = resolve(load("layerzero_config_unresolved.json"))
    assert unresolved.status == "UNRESOLVED"
    assert "effective receive configuration could not be reconstructed" in unresolved.warnings

    print("PASS explicit configuration precedence")
    print("PASS empty app config resolves through receive-library default")
    print("PASS unresolved configuration remains UNKNOWN/UNRESOLVED")
    print("RESULT LayerZeroEffectiveConfigResolver = PASS")

if __name__ == "__main__":
    main()
