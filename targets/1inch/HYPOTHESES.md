# 1inch Limit Order Protocol — Hypothesis Register

**Snapshot:** 2026-09-29  
**Target:** `1inch/limit-order-protocol`  
**Current working release:** tag `4.3.4` → tag object `0a40e01befff19d925457b55191900fb456c2dd2` → commit `7da29889efa2e635611e1caf60f85f595ff7f05f`

**Historical baseline:** tag `4.3.2` → commit `67c56aee3b6a9f4982bf487084bd8da1f6638da0`

## Status vocabulary

- `RECONNAISSANCE`: surface identified; no attack claim.
- `HYPOTHESIS`: falsifiable security property under investigation.
- `REPRODUCED`: observed deterministically against the pinned target in an allowed local test environment.
- `IN-SCOPE`: reproduced effect also satisfies the current bounty impact/scope wording.
- `SUBMITTED`: external report sent.
- `ACCEPTED`: target/triage accepted the report.
- `PAID`: reward actually received.
- `REJECTED`: externally rejected or ruled out; preserve reason.

## H-A1 — Mixed partial-fill accounting

**Security property**

For every valid fill sequence, cumulative maker-side transfer and the protocol's remaining-making state must remain consistent with the order's encoded making amount and fill semantics.

**Probe family**

Use combinations of:

- first fill vs subsequent fill;
- partial vs full requested amount;
- maker-amount vs taker-amount driven filling;
- repeated fills at boundary amounts;
- incompatible or edge-case maker traits, only where the public release permits them.

**Falsification condition**

A deterministic sequence causes the contract to:

1. transfer more maker value than the order permits;
2. leave a remaining amount inconsistent with the actual transferred amount; or
3. permit a later fill that contradicts the intended remaining-state invariant.

A revert, rounding result, or state transition that remains within the documented semantics is not a finding.

**Status:** HYPOTHESIS

## H-B1 — Invalidation composition

**Security property**

Cancellation/invalidation mechanisms must compose without making an invalidated order fillable again or corrupting the invalidation state.

**Probe family**

Compare valid interactions among:

- single-order cancellation;
- mass bit invalidation;
- epoch/series invalidation;
- repeated invalidation;
- boundary nonce/epoch/bit positions.

**Falsification condition**

A deterministic pre-state + call sequence makes an order fillable after an invalidation that should make it permanently unfillable, or produces a state corruption that allows an equivalent bypass.

**Status:** HYPOTHESIS

## H-C1 — Authorization / domain equivalence

**Security property**

A valid signature must remain bound to the intended order fields, EIP-712 domain, and private-order sender constraint across all public fill entry points.

**Probe family**

Compare equivalent order execution through the different fill families, especially:

- `fillOrder`;
- `fillOrderArgs`;
- contract-signature variants;
- private-order / allowed-sender configurations;
- chain/domain changes in local test fixtures.

**Falsification condition**

A signature or authorization accepted in one path can be reused in a distinct security context that changes the intended signer, domain, order, or allowed sender without the required authorization.

**Status:** HYPOTHESIS

## H-D1 — Dynamic calldata interpretation

**Security property**

Extension / args parsing must not reinterpret attacker-controlled calldata so that security-sensitive fields (target, extension, interaction, permit) acquire unintended meaning.

**Probe family**

Exercise:

- empty vs non-empty args;
- extension-present vs extension-absent paths;
- boundary offsets and lengths;
- target/interaction combinations;
- malformed or truncated layouts that remain ABI-decodable.

**Falsification condition**

A deterministic calldata construction, reachable through an authorized public entry point, changes the security meaning of the order or causes unauthorized value transfer / authorization bypass.

Parser oddities without a reachable economic or authorization impact remain non-findings.

**Status:** HYPOTHESIS

## Promotion rule

No hypothesis may advance to `REPRODUCED` without:

- exact target tag + commit;
- exact test command and environment;
- deterministic reproduction;
- observed before/after state;
- minimized sequence;
- independent rerun or second implementation check.

No hypothesis may advance to `IN-SCOPE` without a fresh comparison against the current Immunefi program wording and exclusions.

## Current disposition

No vulnerability is established. The next discriminating action is an executable local harness against the pinned release, with mutation controls around the four probe families.


## H-E1 — Native-order clone / patched-hash equivalence

**Why this is new in 4.3.4**

4.3.4 introduces NativeOrderFactory + NativeOrderImpl. The order is initially hashed with the maker's EOA, the factory derives a deterministic clone address from that hash, then the effective order used by the Limit Order Protocol replaces maker with the clone address. NativeOrderImpl.isValidSignature() reconstructs the original order from the ERC-1271 signature bytes, re-derives the clone, patches maker, and hashes again.

**Security property**

The ERC-1271 acceptance relation must be one-to-one with the exact native order committed by the factory.

**Probe family**

For one created clone, compare:

- exact original order encoded in the signature;
- individual mutations of salt, maker, receiver, makerAsset, takerAsset, makingAmount, takingAmount, and makerTraits;
- boundary values for packed address/trait fields;
- exact patched-order hash vs factory event hash;
- malformed/truncated signature byte strings.

**Falsification condition**

A mutated or malformed order/signature pair is accepted by the clone as a valid signature for an order whose security-relevant fields differ from the factory-committed order.

A rejection, including a clean 0x00000000 ERC-1271 response for malformed input, is expected behavior.

**Status:** HYPOTHESIS

## H-E2 — Native-order collateral / cancellation accounting

**Security property**

For a native order, collateral deposited into the deterministic clone must not become withdrawable by an unauthorized caller, and cancellation must distribute only the clone's actual collateral subject to the documented resolver reward rules.

**Probe family**

Compare:

- full fill;
- partial fill followed by maker cancellation;
- expiry + resolver cancellation with and without reward;
- undercollateralized expiry cancellation where `C < R` and an external WETH top-up brings the clone balance to the reward cap;
- repeated cancellation;
- unauthorized withdraw;
- mutated maker order supplied to validateOrder.

The undercollateralized case is specifically tracked as an economic edge: determine whether the resolver reward can consume maker collateral once a third party supplies only the missing WETH needed to reach the reward cap.

**Falsification condition**

A deterministic local sequence permits an unauthorized withdrawal, over-reward, collateral duplication, or cancellation of a different order's clone.

**Status:** HYPOTHESIS

## H-F1 — Permit2Proxy authorization boundary

**Why this is new in 4.3.4**

Permit2Proxy exposes a deliberately unusual function selector equal to IERC20.transferFrom, allowing it to be used as a maker-asset endpoint while delegating the transfer to Permit2.

**Security property**

Only the Limit Order Protocol can invoke the proxy transfer entry point, and the parameters ultimately authorized by Permit2 remain bound to the signed permit.

**Probe family**

Use local-only negative controls for:

- direct non-LOP caller;
- permitted token differing from the order maker asset;
- requested amount greater than the signed permitted amount;
- expired permit;
- reused permit nonce;
- malformed suffix/extension combinations.

**Falsification condition**

A caller outside the LOP, or an order path with mismatched authorization parameters, can make the proxy transfer assets without a corresponding valid Permit2 authorization.

**Status:** HYPOTHESIS
