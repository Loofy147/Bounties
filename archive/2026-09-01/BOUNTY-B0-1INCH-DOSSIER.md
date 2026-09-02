# B0 Audit Dossier — 1inch Limit Order Protocol

**Snapshot date:** 2026-09-01

This is a reconnaissance dossier, not a vulnerability report. It defines a controlled path for local-only investigation of an in-scope 1inch target.

## Target and eligibility boundary

The 1inch Smart Contracts bounty was live at the snapshot. Its scope listed Limit Order Protocol, Limit Order Settlement, Token-plugins, Farming Contracts, Delegating Contracts, Cross-chain Swap, Solana Crosschain and Solana Fusion. The program applied only to the latest tag/releases, required a PoC and KYC, and its listed low-tier reward started at $100. Eligibility, impact wording, known-issue exclusions and submission rules must be re-verified immediately before any submission.

The Limit Order Protocol repository explicitly warned that `master` was work-in-progress and not audited. Its README identified tag `4.3.2` as a production version. Therefore the working source pin for this dossier was:

```text
repository: 1inch/limit-order-protocol
tag: 4.3.2
working rule: never analyze master as the bounty target
```

## Primary reconnaissance target

`1inch/limit-order-protocol`

Initial study target: `4.3.2`.

The protocol implements signed off-chain limit orders filled on-chain. The target surface included partial and multiple fills, configurable receivers, predicates, pre/post interactions, permit/permit2 flows, WETH handling, private taker restrictions, expiration, and nonce/epoch cancellation.

## Audit surface

### A. Fill accounting

Primary functions:

- `fillOrder` / `fillOrderArgs` entry points;
- `_fillOrder` signature and remaining-amount checks;
- `_checkRemainingMakingAmount`;
- `_fill` amount calculation and invalidation.

**Invariant A1:** across any admissible fill sequence, cumulative maker-side value transferred cannot exceed the order's encoded making amount, and every state transition remains consistent with the selected fill mode.

**Experiments:** single fill; exact boundary fill; two partial fills; many small fills; mixed making/taking amount modes; final fill followed by replay; amount/threshold edge cases.

### B. Invalidation

Relevant paths:

- `cancelOrder`;
- `cancelOrders`;
- `bitsInvalidateForOrder`;
- `_checkRemainingMakingAmount`;
- remaining invalidation and epoch/series mechanisms.

**Invariant B1:** once an order is invalidated by its selected mechanism, no later admissible fill may consume value from the invalidated state.

**Invariant B2:** invalidation mechanisms must not accidentally disable the wrong order class or allow a mode transition to bypass cancellation state.

**Experiments:** fill/cancel race; cancel before first fill; cancel after partial fill; bit invalidation mask boundaries; epoch/series changes; repeated cancellation; mixed invalidation modes.

### C. Authorization and domain separation

Relevant paths:

- `hashOrder`;
- domain separator construction;
- signature verification;
- allowed-sender/private-order restrictions.

**Invariant C1:** an order signature must bind to the intended domain and order data; changing domain, maker, verifying contract or chain context must not create unintended authorization.

**Invariant C2:** a private order's allowed-sender constraint must remain enforced across every fill entry point and argument-parsing variant.

**Experiments:** first-fill signature versus subsequent-fill replay; domain separation changes; `fillOrder` versus `fillOrderArgs`; allowed-sender boundary encodings; contract-order edge cases.

### D. Extension, predicate and callback boundary

Relevant paths:

- `order.isValidExtension(extension)`;
- `checkPredicate`;
- `_parseArgs`;
- pre-interaction parsing;
- taker interaction dispatch;
- post-interaction dispatch;
- token-transfer suffix parsing.

**Invariant D1:** attacker-controlled extension/calldata lengths cannot cause a valid order to be reinterpreted as a different extension or interaction layout.

**Invariant D2:** callback execution cannot invalidate accounting, authorization or cancellation assumptions established earlier in the fill.

**Experiments:** zero/short/overlong argument layouts; extension-length boundary values; interaction-length boundary values; predicate return 0/1/revert; documented callback/re-entry paths; transfer suffix variations.

## Existing audit context

The project's public audit archive must be used as a filter before submission. A previous audit or known issue does not automatically prove the current implementation correct, but an equivalent published issue may make a bounty report ineligible.

Archive: https://github.com/1inch/1inch-audits

## First-pass hypotheses

These remain falsifiable research questions, not allegations.

### H1 — Fill-accounting invariant

For every valid fill sequence, maker remaining amount, taker amount and invalidator state must evolve consistently across repeated, partial and mixed fills. No admissible sequence may produce more maker-asset outflow than the order permits.

### H2 — Invalidation invariant

Once an order is invalidated through its selected mechanism, no later admissible fill path may consume remaining value from that order. Special attention: interactions between bit invalidation, remaining invalidation and epoch/series invalidation.

### H3 — Authorization/domain invariant

A signature or order authorization valid for one maker, receiver, chain, domain, verifying contract or allowed sender must not become valid in an unintended context.

### H4 — Parser/callback consistency

All semantically equivalent fill entry points must preserve the same authorization, amount-accounting and callback invariants. Input slicing or callback-selected targets must not create a security-relevant semantic fork.

## First experiment order

```text
1. pin exact release
2. baseline existing tests
3. construct one-order state model
4. prove A1 on simple fill sequences
5. stress invalidation transitions (B1/B2)
6. stress signature + allowed-sender transitions (C1/C2)
7. stress calldata/extension parser boundaries (D1)
8. stress callbacks and re-entry assumptions (D2)
9. only then add seeded fuzzing
10. compare any candidate with audits + bounty scope
```

The first goal is not a high-severity exploit. The first goal is one small, deterministic, admissible result that survives the entire evidence gate.

## Reproduction protocol

All work must remain local and use only the eligible source/tag and permitted fork/test environment.

```text
pin release
  -> build clean environment
  -> read specification/tests
  -> map state variables
  -> state invariant
  -> construct minimal sequence
  -> run local test
  -> compare with expected economic/security impact
  -> check scope + known issues
  -> minimize PoC
  -> submit only when all gates pass
```

## Evidence package

Every serious candidate should contain:

- exact repository and tag/commit;
- exact contract/function path;
- invariant or intended behavior being violated;
- minimal pre-state;
- exact transaction/call sequence;
- observed post-state;
- deterministic local PoC;
- impact calculation tied to bounty wording;
- known-issue/audit comparison;
- explanation of why the result is not excluded by current scope.

## Stop conditions

Stop the investigation when:

- the code is not part of the eligible release;
- the impact is only theoretical;
- the finding is already documented as a known issue or previous audit finding;
- the result depends on an out-of-scope privileged capability or prohibited activity;
- reproduction cannot be made deterministic;
- the only demonstrated effect is a best-practice or style concern.

## Current conclusion

**B0 target remains active and well-defined. No vulnerability has been established.**

The useful result of the first pass is the reduction of the target into four invariant families — accounting, invalidation, authorization/domain, and parser/callback consistency — each with a deterministic experiment sequence.
