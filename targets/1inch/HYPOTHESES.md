# 1inch Limit Order Protocol — Hypothesis Register

**Snapshot:** 2026-09-29  
**Target:** `1inch/limit-order-protocol`  
**Eligible working release:** tag `4.3.2` → tag object `8b8f05736b857129da3a52a37623a40af05e225d` → commit `67c56aee3b6a9f4982bf487084bd8da1f6638da0`

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
