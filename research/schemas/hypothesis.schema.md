# Hypothesis Record v0.1

```yaml
id: H-YYYYMMDD-NNN
status: RECONNAISSANCE | HYPOTHESIS | REPRODUCED | IN-SCOPE | SUBMISSION-READY | SUBMITTED | ACCEPTED | PAID | REJECTED
target:
  name: string
  version: string
  commit_or_digest: string
scope_basis: string
surface:
  components: []
  functions_or_endpoints: []
invariant: string
attacker:
  capability: string
  prerequisites: []
expected_violation: string
experiment:
  objective: string
  steps: []
  safety_constraints: []
evidence_required: []
result:
  observed: string
  reproducible: false
  impact: string
  novelty: string
rejection_reason: null
review:
  human_confirmed: false
  reviewer: null
```

## State transition rule

A status transition requires its gate evidence. `HYPOTHESIS → REPRODUCED` requires an observed security-relevant effect under the recorded preconditions; `REPRODUCED → IN-SCOPE` requires explicit program scope evidence; `IN-SCOPE → SUBMISSION-READY` requires validated impact, reproducibility, novelty check, and human review readiness.
