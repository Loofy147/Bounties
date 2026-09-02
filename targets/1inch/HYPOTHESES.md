# B0 — Hypothesis Ledger

**Target:** 1inch Limit Order Protocol `4.3.2`
**Status:** research only; no finding established

Each record is a falsifiable hypothesis. A code smell is not promoted without a reproducible security effect.

## H-A1 — mixed partial-fill accounting

**Invariant**

For an order with encoded `makingAmount = M`, the sum of successful fills must never cause cumulative maker-side outflow to exceed `M`, regardless of fill ordering, partial/full mode, amount direction, or repeated attempts.

**Surfaces**

- `OrderMixin._fill`
- `_checkRemainingMakingAmount`
- `RemainingInvalidatorLib.remains`
- `AmountCalculatorLib.getMakingAmount`
- `AmountCalculatorLib.getTakingAmount`

**Adversarial dimensions**

- requested amount `0`, `1`, `M-1`, `M`, `M+1`
- repeated partial fills
- maker-amount vs taking-amount mode
- rounding boundaries
- maximal uint values in isolated local tests
- callback/reentrancy attempts against the already-consumed remaining state

**Required evidence**

1. pinned 4.3.2 target;
2. deterministic initial order state;
3. exact fill sequence;
4. remaining invalidator values after each successful call;
5. token balance deltas;
6. proof that the sequence is attacker-reachable;
7. minimized reproducible PoC.

**Current status:** HYPOTHESIS — no violation demonstrated.

## H-B1 — invalidation composition bypass

**Invariant**

Once an order is invalidated through its applicable mechanism, no alternate entry path or state transition may make the order fillable again.

**Surfaces**

- `cancelOrder`
- `cancelOrders`
- `bitsInvalidateForOrder`
- `BitInvalidatorLib`
- `RemainingInvalidatorLib`
- epoch/series checks

**Current status:** HYPOTHESIS — no violation demonstrated.

## H-C1 — authorization/domain equivalence

**Invariant**

A valid signature must authorize exactly the intended order/domain, and private sender restrictions must be preserved across all fill entry points.

**Surfaces**

- `OrderLib.hash`
- EIP-712 domain separator
- `fillOrder`
- `fillContractOrder`
- `MakerTraitsLib.isAllowedSender`
- first-fill vs subsequent-fill behavior

**Current status:** HYPOTHESIS — no violation demonstrated.

## H-D1 — dynamic calldata interpretation

**Invariant**

`args`, extension offsets and interaction boundaries must not allow security-sensitive fields to be reinterpreted without violating the order/extension binding or expected parser contract.

**Surfaces**

- `TakerTraitsLib`
- `_parseArgs`
- `ExtensionLib`
- `OffsetsLib`
- `OrderLib.isValidExtension`

**Current status:** HYPOTHESIS — parser edge cases identified; exploitability not demonstrated.

## Research rule

A hypothesis may advance only through:

```text
HYPOTHESIS
→ REPRODUCED
→ IN-SCOPE
→ SUBMISSION-READY
```

A failed reproduction is preserved as negative evidence rather than deleted.
