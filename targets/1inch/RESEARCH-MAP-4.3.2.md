# 1inch Limit Order Protocol 4.3.2 — Research Map

**Status:** RECONNAISSANCE
**Target:** `1inch/limit-order-protocol`
**Pinned tag:** `4.3.2`
**Pinned commit:** `67c56aee3b6a9f4982bf487084bd8da1f6638da0`
**Date checked:** 2026-09-02

## Scope boundary

The live Immunefi 1inch Smart Contracts program explicitly lists **Limit Order Protocol** as an in-scope smart-contract asset. The program states that only the latest tags/releases apply and requires a PoC. Current listed smart-contract impacts range from critical direct theft/permanent freezing/protocol insolvency through lower-severity promised-amount delivery failures and fee-only griefing. Re-check the live policy immediately before any submission.

## Source inventory at 4.3.2

Core contracts identified in the pinned tree include:

- `contracts/LimitOrderProtocol.sol`
- `contracts/OrderMixin.sol`
- `contracts/OrderLib.sol`
- `contracts/extensions/OrderIdInvalidator.sol`
- `contracts/extensions/AmountGetterBase.sol`
- `contracts/extensions/AmountGetterWithFee.sol`
- `contracts/extensions/RangeAmountCalculator.sol`
- `contracts/extensions/DutchAuctionCalculator.sol`
- `contracts/extensions/ChainlinkCalculator.sol`
- `contracts/extensions/FeeTaker.sol`
- `contracts/extensions/ETHOrders.sol`
- `contracts/extensions/Permit2WitnessProxy.sol`
- `contracts/extensions/ERC721Proxy.sol`
- `contracts/extensions/ERC721ProxySafe.sol`
- `contracts/extensions/ERC1155Proxy.sol`
- `contracts/extensions/ApprovalPreInteraction.sol`
- `contracts/extensions/ImmutableOwner.sol`

The repository documentation describes regular limit orders as supporting execution predicates and maker callbacks; RFQ orders support expiration, order-id cancellation and a one-time partial fill. Treat those semantics as state-machine inputs requiring explicit invariant checks.

## Initial invariant families

### A — Fill/accounting

`remainingMakingAmount` must never permit cumulative maker-side delivery above the order's authorized amount. Partial fills, repeated fills, fee paths, extension-selected amounts, and mixed entry points must preserve the accounting invariant.

### B — Invalidation

After cancellation/invalidation, no permitted path may settle the invalidated order. Cross-check order-id invalidation, bit/epoch mechanisms, remaining invalidation state, and replay boundaries.

### C — Authorization/domain

The signed order identity must remain bound to the intended EIP-712 domain and all security-sensitive order fields. Private-order sender/taker restrictions must survive across every relevant fulfillment path.

### D — Parsing/extensions/callbacks

Calldata parsing and extension suffixes must not permit reinterpretation of security-sensitive fields. Callbacks and predicates must not create a path around accounting, authorization or invalidation assumptions.

## Research sequence

```text
source snapshot
→ compile/test baseline
→ map OrderMixin state transitions
→ build one-order executable model
→ derive accounting invariants
→ derive invalidation invariants
→ derive authorization/domain invariants
→ audit parser/extension/callback boundaries
→ mutation benchmark
→ deterministic fuzz/property tests
→ compare against public audits/known issues
→ only then pursue concrete exploit hypotheses
```

## Current conclusion

No vulnerability is established. The repository snapshot and live program boundary are sufficiently defined to begin source-level invariant analysis, but any submission decision requires a fresh program check and a reproducible PoC.
