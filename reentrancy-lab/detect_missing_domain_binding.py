#!/usr/bin/env python3
"""
Custom Slither check: flags any function that recovers a signer via
ecrecover() but never references block.chainid or address(this) anywhere
in its body. That's the exact shape of M6's bug (and, it turns out, M5's
too) -- a signed message that means the same thing on every chain and
every deployment that shares the signer key. Stock Slither's 102 built-in
detectors have no opinion on this; it's a trust-boundary question, not a
syntax pattern.

Usage: python3 detect_missing_domain_binding.py contracts/m6/BridgeDomainSeparation.sol
"""
import sys
from slither import Slither

def check(sol_file):
    json_file = sol_file.replace(".sol", ".input.json")
    sl = Slither(
        json_file,
        compile_force_framework="solc-json",
        solc_working_dir=str(__import__("pathlib").Path(sol_file).parent),
    )
    findings = []
    for contract in sl.contracts:
        for function in contract.functions:
            src_text = " ".join(str(node) for node in function.nodes)
            calls_ecrecover = "ecrecover" in src_text
            binds_domain = "chainid" in src_text.lower() or "address(this)" in src_text
            if calls_ecrecover and not binds_domain:
                findings.append(f"{contract.name}.{function.name}()")
    return findings

if __name__ == "__main__":
    target = sys.argv[1]
    results = check(target)
    if results:
        print(f"[FLAGGED] {target}")
        for f in results:
            print(f"  - {f}: ecrecover() used, but block.chainid / address(this) never referenced in the same function.")
            print(f"    -> signature is valid on every chain and every deployment sharing the signer key.")
    else:
        print(f"[clean] {target} -- no unbound signature recovery found")
