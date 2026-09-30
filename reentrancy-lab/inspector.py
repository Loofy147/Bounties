#!/usr/bin/env python3
"""
inspector.py — point this at ANY .sol file, not just this lab's own modules.

Runs two layers:
  1. Stock Slither, triaged (high-confidence/impact only — see TOOLING.md
     for why the raw output is mostly noise for real auditing).
  2. Five custom detectors, each built from a specific mechanical pattern
     this lab proved Slither's 102 built-in detectors miss, across nine
     real modules:

       unbound-signature        (M5, M6)  ecrecover with no chainid/address(this) bound in
       unprotected-initializer  (M2, M7)  init*-named function sets a privileged var with no msg.sender check
       raw-balance-valuation    (M4)      a price/rate/totalAssets-style function reads raw balanceOf(address(this))
       live-balance-voting      (M8)      voting power pulled from live balanceOf(msg.sender), no snapshot/checkpoint anywhere
       unbounded-swap           (M9)      a swap/trade/exchange function with no min-output/slippage parameter

  Honest limitation, stated rather than hidden: M3's class (spot-price
  oracle manipulation via AMM reserves with no TWAP) is NOT auto-detected
  here. It's a structural/temporal absence — "there's no historical price
  tracking anywhere in this contract" — not a text pattern, and doesn't
  reduce to a cheap heuristic without real dataflow analysis. That's a
  genuine remaining gap, not a false claim of coverage.

Usage: python3 inspector.py <path/to/contract.sol>
"""
import re
import sys
import pathlib
import subprocess
from slither import Slither
from slither.detectors.abstract_detector import AbstractDetector
import slither.detectors.all_detectors as all_detectors

ALL_DETECTOR_CLASSES = [
    obj
    for name in dir(all_detectors)
    if not name.startswith("_")
    for obj in [getattr(all_detectors, name)]
    if isinstance(obj, type) and issubclass(obj, AbstractDetector)
]


def to_standard_json(sol_file: str) -> str:
    subprocess.run(["node", "to_standard_json.js", sol_file], check=True, capture_output=True)
    return sol_file.replace(".sol", ".input.json")


def load(sol_file: str) -> Slither:
    json_file = to_standard_json(sol_file)
    return Slither(
        json_file,
        compile_force_framework="solc-json",
        solc_working_dir=str(pathlib.Path(sol_file).parent),
    )


# ---------- custom detectors ----------

def body_text(function) -> str:
    return " ".join(str(node) for node in function.nodes)


def unbound_signature(contract):
    out = []
    for f in contract.functions:
        t = body_text(f)
        if "ecrecover" in t and "chainid" not in t.lower() and "address(this)" not in t:
            out.append(f"{f.name}(): ecrecover() used, block.chainid/address(this) never referenced -> replayable across chains/deployments")
    return out


def unprotected_initializer(contract):
    out = []
    all_text = " ".join(body_text(f) for f in contract.functions)
    privileged_vars = set(re.findall(r"msg\.sender\s*==\s*(\w+)", all_text) + re.findall(r"(\w+)\s*==\s*msg\.sender", all_text))
    for f in contract.functions:
        if "init" not in f.name.lower():
            continue
        t = body_text(f)
        writes_privileged = any(re.search(rf"\b{re.escape(v)}\b\s*=", t) for v in privileged_vars)
        has_caller_check = "msg.sender" in t
        if writes_privileged and not has_caller_check:
            out.append(f"{f.name}(): sets a privileged variable ({', '.join(privileged_vars)}) with no msg.sender check anywhere in the function -> callable by anyone, any time")
    return out


def raw_balance_valuation(contract):
    out = []
    for f in contract.functions:
        if not re.search(r"price|rate|totalassets|value", f.name.lower()):
            continue
        t = body_text(f)
        if "balanceof(address(this))" in t.lower():
            out.append(f"{f.name}(): reads raw balanceOf(address(this)) directly as a valuation source -> donation/direct-transfer manipulable")
    return out


def live_balance_voting(contract):
    out = []
    contract_text = " ".join(body_text(f) for f in contract.functions).lower()
    has_snapshot = any(kw in contract_text for kw in ["checkpoint", "snapshot", "getpastvotes"])
    if has_snapshot:
        return out
    for f in contract.functions:
        t = body_text(f)
        if "balanceof(msg.sender)" in t.lower() and re.search(r"vote|power", t.lower()):
            out.append(f"{f.name}(): voting power pulled from live balanceOf(msg.sender), no snapshot/checkpoint found anywhere in the contract -> flash-loanable")
    return out


def unbounded_swap(contract):
    out = []
    for f in contract.functions:
        if not re.search(r"swap|trade|exchange", f.name.lower()):
            continue
        param_names = " ".join(p.name.lower() for p in f.parameters)
        if not re.search(r"min|slippage", param_names):
            out.append(f"{f.name}(): no min-output/slippage parameter -> sandwichable, victim accepts whatever price exists at execution time")
    return out


CUSTOM_DETECTORS = [
    ("unbound-signature", unbound_signature),
    ("unprotected-initializer", unprotected_initializer),
    ("raw-balance-valuation", raw_balance_valuation),
    ("live-balance-voting", live_balance_voting),
    ("unbounded-swap", unbounded_swap),
]


# ---------- Slither's own detectors, triaged ----------

NOISE_DETECTORS = {"naming-convention", "solc-version", "pragma", "immutable-states", "constable-states"}


def run_stock_slither(sl: Slither):
    findings = []
    for detector_cls in ALL_DETECTOR_CLASSES:
        sl.register_detector(detector_cls)
    results = sl.run_detectors()
    for group in results:
        for r in group:
            if r["check"] in NOISE_DETECTORS:
                continue
            findings.append(f"[{r['check']}] {r['description'].strip()}")
    return findings


def inspect(sol_file: str):
    sl = load(sol_file)
    print(f"\n{'='*70}\nINSPECTING: {sol_file}\n{'='*70}")

    stock = run_stock_slither(sl)
    print(f"\n-- Stock Slither (triaged, {len(stock)} findings) --")
    for line in stock[:8]:
        print(" ", line[:140])
    if len(stock) > 8:
        print(f"  ... and {len(stock) - 8} more")

    print(f"\n-- Custom detectors (this lab's) --")
    any_custom = False
    for name, fn in CUSTOM_DETECTORS:
        for contract in sl.contracts:
            for finding in fn(contract):
                print(f"  [{name}] {contract.name}.{finding}")
                any_custom = True
    if not any_custom:
        print("  (none)")


if __name__ == "__main__":
    inspect(sys.argv[1])
