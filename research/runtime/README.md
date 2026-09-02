# Hunter Runtime v0.1

This directory contains the deterministic execution kernel for bounded security research.

## Guarantees

- scope is checked before execution;
- evidence is content-addressed with SHA-256;
- successive evidence bundles can be hash-linked;
- validation is a separate record from discovery;
- the kernel does not submit reports or bypass program policy.

## Local use

```python
from hunter_runner import HunterKernel, ScopeContract, Experiment, Validation

scope = ScopeContract(
    target_id="local-target",
    version="pinned",
    allowed_assets=("contract",),
    allowed_actions=("read",),
    environment="isolated-local",
)

kernel = HunterKernel(scope)
experiment = Experiment("H-001", "contract", "read", {"expected": 0}, seed=1)
# kernel.execute(experiment, deterministic_runner(your_pure_test))
```

The runtime is intentionally target-agnostic. Target adapters belong outside this kernel.

## Promotion rule

A runtime experiment is not a finding. Promotion requires an independent validation record with all applicable gates green.
