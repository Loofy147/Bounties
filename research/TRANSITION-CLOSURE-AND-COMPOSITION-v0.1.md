# Transition-Closure Gaps and Cross-Operation Invariant Composition — v0.1

**Status:** REUSABLE RESEARCH METHOD / CASE STUDY  
**Reviewed:** 2026-10-25  
**Scope:** Solidity/EVM and other stateful systems with accounting, authorization, eligibility, or settlement transitions  
**Finding status:** This document asserts no vulnerability in any current bounty target.

## 1. Purpose

Use this pattern when a protocol exposes several individually legitimate operations whose composition can violate a system-level invariant. The key review question is not only “does this function do what its name says?” but also:

> After every externally reachable state transition, can the resulting state be exploited by another allowed operation to extract value, bypass authorization, or violate an accounting/risk invariant?

The method is called **transition-closure review**. It checks that the protocol's validation rules cover the complete set of state transitions that can affect a security property, including newly added methods, alternate entry points, exceptional branches, and interactions between functions.

This is a research heuristic. A missing check is a lead, not a finding. The violated property, reachable state, actual impact, target eligibility, and known-issue status must all be independently established.

## 2. Evidence-grounded case study: Euler V1, March 2023

### ESTABLISHED

Euler's own retrospective reports that the March 13, 2023 exploit extracted approximately $197 million in assets. Euler states that the funds were subsequently returned during the recovery effort, with approximately $240 million in assets returned as their market value changed. Do not conflate the initial extraction with the later recovery. Source: [Euler Labs, “War & Peace: Behind the Scenes of Euler’s $240M Exploit Recovery”](https://www.euler.finance/blog/war-peace-behind-the-scenes-of-eulers-240m-exploit-recovery), published 2024-01-10.

The Euler account says **donateToReserves** was added as part of a fix for a previous first-depositor issue. The team states that the change had been reviewed; the function's critical omission was a health check ensuring that a user could not make their existing account unhealthy simply by donating collateral to reserves. The attacker used that state transition to make a position liquidatable, then used the liquidation mechanism to obtain a bonus exceeding the cost of the donation. This is a cross-operation invariant failure, not a claim that every donation or liquidation implementation is independently defective.

The contemporaneous governance proposal [eIP-14: Contract Upgrades](https://forum.euler.finance/t/eip-14-contract-upgrades/305), dated 2022-07-06, lists donateToReserves as an EToken feature and describes its intended uses. It provides useful change-history context; it does not alone establish what the audits did or did not cover.

### INTERPRETATION

- **ESTABLISHED:** A user-controlled operation could reduce collateral without the expected post-transition health check, and a later liquidation operation converted the resulting state into value.
- **ESTABLISHED:** The affected feature had a legitimate purpose and was introduced in a change intended to repair another issue.
- **INFERENCE:** Cross-entrypoint invariant coverage and sequence-level tests are useful ways to search for analogous classes of defects.
- **HYPOTHESIS:** A different protocol may contain a transition-closure gap if its state-changing entry points enforce a security property asymmetrically. This must be tested against that protocol's own semantics.
- **UNKNOWN until examined per target:** Whether any current bounty target contains such a gap; whether a candidate is reachable, novel, in scope, or reportable.

The historical case is an instructional benchmark only. It is not evidence of a defect in 1inch, SP1, or another current bounty target.

## 3. Formal model

Represent a protocol as a state transition system:

~~~text
S' = f(S, actor, input)
~~~

where S is protocol state, actor is the set of capabilities used, input is the operation input, and S' is the resulting state.

Define a security-relevant projection of state. For a lending protocol, it may include:

- collateral value and collateral eligibility;
- debt and accrued liabilities;
- account health or liquidation eligibility;
- reserves, share balances, and claimable amounts;
- amounts a liquidator or other actor can receive;
- total assets and liabilities for the affected market.

For other protocols, substitute their actual state variables: order fills and remaining amounts, vault assets and shares, bridge message state, signer/nonce state, claim accounting, or upgrade authority.

Do **not** assume a universal rule that every account must always be solvent. Prices can change, and liquidation or default transitions may explicitly handle unhealthy accounts. Instead, derive the valid postcondition from the target specification:

- user-controlled transitions that worsen health must satisfy the documented health gate, **or**
- an explicit, intended exception must apply, with the downstream protocol rules preventing that exception from becoming an unintended extraction path.

The protocol must also preserve the relevant accounting/authorization invariants across sequences of allowed transitions.

## 4. Invariant families

### I-1 — Transition-closure

For every externally reachable state-changing operation, identify whether it can reduce collateral, increase debt, change asset eligibility, increase withdrawal/claim capacity, alter reserve ownership, change liquidation eligibility, or otherwise worsen a protected risk measure.

Each such transition must either enforce the applicable postcondition or be covered by a documented exception whose downstream consequences are safe.

A check in one sibling function does not establish that all semantically equivalent paths are protected. Check the actual path, including branches and internal calls.

### I-2 — Accounting conservation

Token movements, internal balances, reserves, shares, debt, fee accrual, and claims must reconcile according to the protocol's own accounting model. A value reclassification (for example, user-owned balance to protocol reserves) must not silently make a later payout exceed the intended entitlement or shift a loss to another party without an explicit rule.

### I-3 — Composition safety

A bounded sequence of individually allowed calls must not create a state that enables an actor to extract more value or authority than the protocol's intended rules permit.

Review both:
- **local properties:** preconditions/postconditions of each operation;
- **sequence properties:** outcomes after two or more operations, including atomic compositions within one transaction where the platform permits them.

### I-4 — Capability/identity realism

Model permissions explicitly. Do not assume that borrower, liquidator, resolver, relayer, keeper, and receiver must be different parties unless the contract enforces that distinction. Conversely, do not assume a role is attacker-controlled without evidence. Test only capabilities that exist in the permitted threat model.

### I-5 — Upgrade/change closure

For upgrades and new entry points, diff state variables, externally reachable mutators, authorization checks, invariant checks, callbacks, and downstream consumers. A new operation that touches an existing invariant is part of that invariant's review surface, even if the change request targets another bug.

### I-6 — Economic accounting

If an economic effect is claimed, measure separately:
- value lost by the victim or protocol;
- value received by the actor;
- capital supplied or returned;
- fees, rewards, gas, and transaction costs;
- protocol bad debt or reserve shortfall.

Gross transfer, victim loss, protocol loss, and actor profitability are different quantities. Low attacker ROI alone neither proves nor disproves a security invariant violation; it is a separate feasibility consideration.

## 5. Controlled investigation procedure

1. **Pin and scope the target.** Record exact repository, tag/release, commit, dependency state, deployed asset correspondence where required, official program scope, current known-issue exclusions, and allowed environment. Reject ambiguous or unauthorized targets before testing.
2. **Build a mutation inventory.** List every externally reachable function that can change one of the invariant-relevant state variables. Include batch entry points, wrappers, callbacks, delegated calls, privileged methods, and newly introduced functions.
3. **Map validation coverage.** For each operation, record its required preconditions, internal accounting changes, checks before and after mutation, emitted events, and downstream functions whose behavior it can influence. A missing check becomes a hypothesis, not a conclusion.
4. **Write the invariant before the probe.** Specify a predicate or state relation that can be falsified from observable state. Document the allowed exceptions.
5. **Build the smallest local state model.** Start from valid protocol-generated state. Avoid arbitrary storage edits or invented account states unless the test is explicitly a separate unit test of an internal primitive.
6. **Exercise operation boundaries.** Compare related entry points and the same operation with boundary amounts, empty/non-empty balances, residual positions, and relevant authorization states.
7. **Exercise bounded compositions.** Where explicitly permitted, test sequences that create a position, change its risk/accounting state, then invoke a downstream operation that can settle, liquidate, redeem, withdraw, or pay out. Enumerate actor identity/role variants permitted by the threat model. Flash liquidity, if used, is a funding primitive—not the root-cause explanation.
8. **Run negative controls.** Include healthy-state controls, authorization-denied controls, and sequences that should revert under the specification. Verify the target baseline first.
9. **Validate harness sensitivity.** Add a deliberate test-oracle or model mutation that removes the relevant postcondition, then show that the test suite detects the weakened property. Keep mutants out of the target code and evidence for real behavior separate from mutation-test evidence.
10. **Minimize and independently rerun.** Reduce call count, input complexity, state complexity, and amounts while preserving the same violation. Re-run from a clean pinned baseline and preserve raw evidence.
11. **Close scope and novelty gates.** Compare relevant audit reports, known issues, change history, and official impact definitions. Record initial discovery time immediately. A deadline is a hard gate; a later page change does not reset a clock unless the program explicitly says so.
12. **Human review.** A human researcher must validate the claim, scope interpretation, impact calculation, policy compliance, and final report. Never submit an AI-generated report where the program prohibits it.

All tests must remain local/fork-only whenever the active program requires that boundary. Never test production or public test networks contrary to current program rules.

## 6. Experiment record template

Use this as a starting record for a new target-specific hypothesis. It is not itself evidence.

~~~yaml
claim_id: "TCG-<target>-<sequence>"
classification: HYPOTHESIS
target:
  repository: null
  tag_or_release: null
  commit: null
  asset_or_contract: null
scope:
  official_information_url: null
  official_scope_url: null
  permitted_environment: null
  impact_wording: null
  report_deadline_rule: null
invariant:
  statement: null
  state_variables: []
  documented_exceptions: []
threat_model:
  actor_capabilities: []
  prohibited_assumptions: []
experiment:
  baseline_command: null
  fixed_case_or_seed: null
  operation_sequence: []
  expected_postcondition: null
  observed_postcondition: null
evidence:
  pre_state_digest: null
  post_state_digest: null
  raw_artifact_paths: []
  independent_rerun: UNKNOWN
  mutation_control: UNKNOWN
impact:
  victim_loss: UNKNOWN
  protocol_loss: UNKNOWN
  actor_receipt: UNKNOWN
  fees_and_costs: UNKNOWN
  in_scope_mapping: UNKNOWN
novelty:
  audits_checked: []
  known_issues_checked: []
  source_history_checked: []
  result: UNKNOWN
eligibility:
  first_discovery_utc: null
  role_or_privilege_gate: UNKNOWN
  reporting_eligibility: UNKNOWN
decision:
  status: HYPOTHESIS
  next_discriminating_test: null
  stop_conditions: []
~~~

Replace UNKNOWN only with supported evidence. Preserve rejected hypotheses and the reason for rejection.

## 7. Promotion and stop gates

- **RECONNAISSANCE:** surface mapped; no claim that a defect exists.
- **HYPOTHESIS:** invariant and falsifiable experiment specified.
- **EXPERIMENTALLY_SUPPORTED:** the specified local behavior was observed reproducibly. This label does not establish exploitability or bounty eligibility.
- **REPRODUCED:** a deterministic security-property violation is demonstrated against the pinned target with preserved evidence and independent rerun.
- **IN-SCOPE:** reproduced impact maps to current official scope and clears the relevant target, environment, impact, and known-issue gates.
- **SUBMISSION-READY:** novelty, deadline, eligibility, evidence, minimization, and human-review gates are clear.
- **SUBMITTED / ACCEPTED / PAID / REJECTED:** only use after the corresponding external event occurs.

Stop or hold when the target is unpinned, scope is unclear, the only evidence is an arbitrary local state, the sequence is not reachable, the postcondition is actually permitted by the design, impact does not follow, an applicable known issue exists, the deadline/eligibility gate is unresolved, or the experiment would violate policy.

## 8. Reusable review checklist

- [ ] Exact asset, release, commit, and test environment pinned.
- [ ] Official scope and current program rules read.
- [ ] All relevant state-mutating entry points enumerated.
- [ ] Shared invariant mapped to each relevant transition.
- [ ] Newly added/changed functions and alternate paths reviewed.
- [ ] Sequence-level properties tested, not only isolated functions.
- [ ] Actor permissions/identity assumptions evidenced.
- [ ] Clean baseline and negative controls pass.
- [ ] Mutation control demonstrates that the test can detect a missing invariant.
- [ ] Pre/post-state deltas and raw evidence preserved.
- [ ] Victim loss, protocol loss, actor receipts, and costs separated.
- [ ] Audit/known-issue and scope-impact comparison completed.
- [ ] First-discovery timestamp and report deadline recorded.
- [ ] Human researcher independently validates every claim and owns any submission.

## 9. Application to the Bounties track

This method directly fits the repository's existing invariant-first loop: state model → invariant → controlled experiment → evidence → independent validation → impact → minimization → scope/novelty gate.

It may inform future research plans for lending, vault accounting, DEX settlement, bridges, and other stateful protocols. It does **not** reopen or strengthen an existing target hypothesis without new target-specific evidence. In particular, it does not change any existing 1inch H-E2 status and must not be used to infer a vulnerability from prior local behavior.

## 10. Primary references

- Euler Labs, [“War & Peace: Behind the Scenes of Euler’s $240M Exploit Recovery”](https://www.euler.finance/blog/war-peace-behind-the-scenes-of-eulers-240m-exploit-recovery), 2024-01-10. Euler's retrospective on the March 2023 exploit, the missing health check, the function's purpose, the liquidation interaction, and the subsequent recovery.
- Euler Governance Forum, [“eIP 14: Contract Upgrades”](https://forum.euler.finance/t/eip-14-contract-upgrades/305), 2022-07-06. Contemporaneous change rationale and the introduction of donateToReserves.

Checked 2026-10-25. These are historical primary sources, not current bounty terms and not evidence about any other target.
