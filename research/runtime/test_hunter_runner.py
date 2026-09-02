from hunter_runner import Experiment, HunterKernel, ScopeContract, Validation, deterministic_runner


def test_scope_blocks_unauthorized_execution() -> None:
    kernel = HunterKernel(
        ScopeContract(
            target_id="t",
            version="v1",
            allowed_assets=("local-contract",),
            allowed_actions=("read",),
            environment="isolated-local",
        )
    )

    try:
        kernel.plan(Experiment("H-1", "remote-host", "write", {}, seed=1))
    except PermissionError:
        pass
    else:
        raise AssertionError("out-of-scope experiment was not rejected")


def test_evidence_is_deterministic_and_hash_linked() -> None:
    kernel = HunterKernel(
        ScopeContract(
            target_id="t",
            version="v1",
            allowed_assets=("contract",),
            allowed_actions=("read",),
            environment="isolated-local",
        )
    )
    runner = deterministic_runner(lambda inputs, seed: inputs["x"] + seed)

    first = kernel.execute(Experiment("H-1", "contract", "read", {"expected": 4, "x": 3}, seed=1), runner)
    second = kernel.execute(Experiment("H-2", "contract", "read", {"expected": 9, "x": 7}, seed=2), runner)

    assert first.observed == 4
    assert second.observed == 9
    assert first.parent_hash is None
    assert second.parent_hash == first.digest()
    assert first.digest() == first.digest()


def test_validation_requires_every_submission_gate() -> None:
    base = dict(
        real=True,
        reachable=True,
        security_property_violated=True,
        impact_demonstrated=True,
        reproducible=True,
        scope_confirmed=True,
        novelty_checked=True,
    )
    assert Validation(**base).submission_ready
    assert not Validation(**{**base, "impact_demonstrated": False}).submission_ready
