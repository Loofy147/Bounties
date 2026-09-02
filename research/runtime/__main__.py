"""Minimal self-check entry point for the zero-dependency Hunter kernel."""
from .hunter_runner import Evidence, Experiment, HunterKernel, ScopeContract, Validation, deterministic_runner


def main() -> None:
    scope = ScopeContract("self-check", "v0.1", ("kernel",), ("read",), "isolated-local")
    kernel = HunterKernel(scope)
    exp = Experiment("SELF-CHECK", "kernel", "read", {"expected": 42, "x": 41}, seed=1)
    evidence = kernel.execute(exp, deterministic_runner(lambda inputs, seed: inputs["x"] + seed))
    validation = Validation(True, True, True, True, True, True, True, "kernel self-check")
    assert evidence.observed == 42
    assert evidence.digest()
    assert validation.submission_ready
    print("Hunter kernel self-check: PASS")


if __name__ == "__main__":
    main()
