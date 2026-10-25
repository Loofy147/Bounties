# WAX Multi-Chain Bridge — Negative Fee and Cross-Domain Accounting Invariant

**Checked:** 2026-10-25  
**Status:** PUBLIC-INCIDENT CASE STUDY / SECONDARY-SOURCE EVIDENCE  
**Finding status:** No new vulnerability is claimed. No live testing was performed or recommended.

## 1. Why this case is useful

The public report about the WAX Multi-Chain Bridge incident of 2026-10-22 describes a different invariant failure from Euler and Wormhole:

- **Euler:** a collateral-reducing transition omitted its required solvency postcondition.
- **Wormhole:** data was accepted without authenticating the identity of the source account that supposedly supplied trusted instruction history.
- **WAX:** a parameter's accepted value domain did not match its intended semantics, allowing the source-side debit and the amount recorded for destination payout to diverge.

The shared lesson is broader than “look for a missing check”: identify the exact relation that must hold between a request, its accounting effect, its evidence/receipt, and the downstream action.

## 2. Evidence and limits

### ESTABLISHED — as reported by public security research

SlowMist's public incident database describes an exploit on 2026-10-22 in WAX Multi-Chain Bridge's `eth.token::withdraw` action. Its summary says the function did not enforce `max_fee >= 0` before computing the source-side debit. A negative `max_fee` equal to the negative of `quantity` could make the computed debit zero while the withdrawal record retained the positive `quantity`, leading to corresponding payouts on Solana and Ethereum. SlowMist estimates losses at approximately $90,500.

Sources:
- [SlowMist incident record — WAX Multi-Chain Bridge](https://hacked.slowmist.io/en/)
- [SlowMist bridge incident index](https://hacked.slowmist.io/?c=Bridge)

These are security-research sources, not WAX's own postmortem. Amount estimates differ across reporting, so do not treat one dollar figure as an on-chain exact invariant.

### UNKNOWN — do not overstate

The public-source review for this note did not establish:
- the official WAX postmortem;
- an authoritative public copy of the exact vulnerable `eth.token` source;
- an immutable fix commit or deployed fixed version;
- the current bridge status and whether the relevant route remains paused;
- any bounty program, safe harbor, or authorization to test.

Thus, the source-level mechanism above remains attributed to SlowMist's report. No exploit test or transaction replay was performed for this document.

## 3. State the invariant precisely

“Withdrawal debit must always be strictly positive” is too broad as a universal rule: some systems may legitimately support zero-amount bookkeeping operations. The meaningful invariant is conditional:

> If a successful source-chain operation records an externally payable withdrawal amount (q > 0), the source-side accounting must apply the documented, authorized debit/lock/burn needed to justify that liability, and the amount accepted by the destination payout path must be bound to that same accounting transition.

For an asset where the source debit is defined as (d = q + f), with `q` the withdrawal quantity and `f` a non-negative maximum-fee amount in the same asset unit, the following should hold under that protocol's semantics:

- `q > 0`;
- `f >= 0`;
- asset symbol/precision and account identity match the withdrawal;
- `d` is representable and satisfies the required debit semantics;
- an accepted payout record for `q` cannot be created if the source-side accounting did not perform the corresponding authorized debit/lock/burn;
- if the fee is zero, the range validation on the user-supplied maximum fee is still enforced. A zero configured fee must not disable validation of a parameter's domain.

Do not blindly enforce this exact equation on another bridge. First derive whether the source ledger uses burn, debit, lock, escrow, or a separate fee token. Then encode that model as a conservation/reconciliation relation.

## 4. Failure model

The reported failure can be represented at a semantic level without reproducing it against any live bridge:

~~~text
Inputs: positive withdrawal quantity q; caller-controlled max-fee parameter f

Expected:
  validate q and f domains
  validate asset/precision and fee policy
  apply authorized source-side accounting
  create a payout record bound to the accounted amount
  destination adapter verifies that record and pays the same authorized amount

Reported inconsistency:
  the accepted parameter domain allowed f < 0
  source-side debit arithmetic could cancel q
  payout record still represented the positive q
  downstream bridge accepted the record as the basis for release
~~~

The root cause is not merely “an arithmetic result equals zero.” It is **a mismatch between the value debited on the source ledger and the external liability asserted to the bridge**. The negative parameter and conditional fee-check path are the reported way that mismatch became reachable.

## 5. Detection rule specification

### WAX-INV-01 — Parameter-domain / semantic-type consistency

For every fee, bound, delta, discount, or adjustment parameter:
- record its declared type and actual representable domain;
- record its business meaning and permitted mathematical domain;
- validate the domain unconditionally before branches that depend on configured values;
- validate unit/symbol/precision compatibility before arithmetic;
- check overflow/underflow and signed-to-unsigned conversion boundaries.

A type allowing negative values does not make negative values semantically valid for a fee. Use a non-negative representation where practical; otherwise assert the range explicitly.

### WAX-INV-02 — Debit-to-liability correspondence

For each successful outbound request, reconcile:
- recorded payout quantity;
- source-side balance debit, burn, or lock;
- fee amount and fee recipient;
- event/message fields consumed by relayers;
- destination-chain release amount and recipient.

Alert when `payout_quantity > 0` but the source-side accounting delta is zero or lower than the protocol's documented required amount, unless an explicit, audited protocol rule accounts for the difference.

This rule must compare state and accounting evidence, not just event presence. An event can be emitted while the intended value movement is absent.

### WAX-INV-03 — Atomic accounting/receipt binding

An event or bridge record representing a payable action must only persist if the corresponding source-side accounting transition succeeds and is committed in the same transaction boundary. If execution aborts, neither the accounting claim nor the releasable message may survive.

Where source and destination chains cannot share atomic transaction state, a destination release must validate authenticated source evidence that is bound to a unique message/nonce, asset, quantity, destination, and the source-side accounting transition.

### WAX-INV-04 — Branch-independent input validation

Validation of attacker-controlled inputs must not be bypassed just because:
- configured fees are zero;
- an optional fee operation is skipped;
- an alternate route or token symbol is selected;
- the function takes a fast path;
- a batch path uses a different helper.

Mutation-test the validator by weakening one constraint at a time and verify that the same test suite detects the defect.

## 6. Test properties for owned or expressly authorized environments

This is a test specification, not authorization to probe WAX or any external bridge.

1. Valid positive withdrawal with zero configured fee: source accounting and destination liability reconcile.
2. Valid positive withdrawal with positive fee: source debit and fee accounting reconcile.
3. Negative fee input: rejected before recording any payable withdrawal.
4. Zero withdrawal: behavior follows the written specification; no external payout may be inferred from a zero debit without an explicit rule.
5. Quantity/fee symbol or precision mismatch: rejected.
6. Arithmetic boundary: overflow, underflow, and invalid conversion fail atomically.
7. Forced accounting failure: no releasable bridge record survives.
8. Replay or duplicate message: the destination cannot release twice for one source-side accounting transition.
9. Event/state consistency: emitted events and stored messages match post-state accounting; events alone are not accepted as proof.
10. Test-oracle mutation: removing the domain guard or debit/record correspondence must make the test fail.

Do not test a live or restarted WAX bridge absent current, explicit authorization and an agreed environment.

## 7. Cross-case invariant matrix

| Case | Invariant | Defect class | Detection focus |
|---|---|---|---|
| Euler V1 | Every collateral-reducing user transition enforces or safely accounts for its postcondition on account health | Missing post-transition guard | Mutation-to-check coverage and downstream liquidation composition |
| Wormhole Solana bridge | Trusted instruction evidence must come from the canonical Instructions sysvar and the expected verification program/message | Source/provenance validation failure | Fake account identity negative controls and independent program/message binding |
| WAX Multi-Chain Bridge | Any external payout record must be justified by matching, authorized source-ledger accounting; a fee parameter must remain in its valid domain | Parameter-domain mismatch plus accounting/receipt divergence | Range, unit, debit/record reconciliation, and atomicity checks |
| Initia incident | Spendable balance increases must have authorized VM state-write provenance and bridge redemptions must match valid backing/accounting evidence | Reported execution-state integrity failure; exact patch path unknown in the public source snapshot | Cache/session equivalence, state-write attribution, and asset-specific conservation |

The Initia row records a public-incident research theme only; it is not evidence of an additional flaw or a verified current target.

## 8. Evidence labels

- **ESTABLISHED:** SlowMist publicly described the WAX incident and its negative-`max_fee` / debit-to-record mechanism.
- **EXPERIMENTALLY_SUPPORTED:** No local reproduction or independent chain replay was performed for this document.
- **INFERENCE:** The detection rules generalize from the reported mechanism to similar accounting/receipt boundaries.
- **HYPOTHESIS:** A separately authorized implementation may contain a similar mismatch; it requires target-specific proof.
- **UNKNOWN:** Exact vulnerable source revision, definitive project postmortem, deployed patch, current operational state, and bounty/testing eligibility.

## 9. Primary follow-up, if this case is ever pursued

1. Locate a WAX project-authored incident statement and exact source/fix revision.
2. Establish whether the public report is complete and whether a regression test already covers the issue.
3. Do not re-report the already-public incident as a novel discovery.
4. Do not run live tests. Any separate research requires explicit program scope, written authorization where needed, and a local/controlled environment.
5. Validate a distinct future claim against the exact authorized version, with minimal deterministic evidence and human review.

Checked 2026-10-25. This document is defensive research methodology, not a bounty submission or exploit claim.
