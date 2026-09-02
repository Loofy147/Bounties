# H-A1 Results — 1inch Limit Order Protocol 4.3.2

## Status

**Model validated; target integration pending.**

This artifact records only the current local reference-model evidence. It is not a vulnerability report.

## Target pin

- Repository: `1inch/limit-order-protocol`
- Working release: `4.3.2`
- Source rule: do not treat `master`/WIP as the bounty target.
- Target integration must re-verify the active bounty scope and eligible release immediately before submission.

## Independent model coverage

The Python model in `accounting.py` is intentionally independent of production helpers.

Covered properties:

1. cumulative maker-side outflow never exceeds encoded maker amount in the correct model;
2. repeated partial fills preserve remaining-maker state;
3. mixed making-mode and taking-mode fills preserve remaining state;
4. filling above remaining amount clamps once;
5. floor/ceil arithmetic follows the intended mode;
6. RemainingInvalidator is the bitwise complement of the remaining maker amount;
7. zero/invalid boundary inputs are rejected by the model;
8. the production `unchecked` ceil branch is represented as an arithmetic control rather than a vulnerability claim.

## Negative control

The `mutated_no_decrement` control deliberately omits the remaining-state decrement. A repeated fill then produces cumulative maker outflow greater than the encoded order amount, demonstrating that the model can detect the targeted defect class.

## Boundary classification

The pinned 4.3.2 `AmountCalculatorLib.getTakingAmount` contains a low-128-bit `unchecked` arithmetic branch. A wraparound case can produce a zero calculator result. The relevant downstream `OrderMixin` path rejects zero-value fills.

**Disposition:** boundary behavior only; no security finding established.

## Next gate

Connect the independent model to an isolated local fork / compiled 4.3.2 environment and compare:

- initial state;
- exact fill sequence;
- requested and executed amounts;
- remaining amount;
- invalidator state;
- maker/taker balance deltas;
- revert behavior.

No remote or public-network testing is part of this gate.
