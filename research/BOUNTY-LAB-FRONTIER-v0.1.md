# Bounty Research + Lab Frontier v0.1

Date: 2026-10-06
Repository: `Loofy147/Bounties`
Baseline branch: `feat/reentrancy-lab`
Tracking branch: `research/usdt0-lab-frontier-v0.1`
Primary active target: USDT0
Secondary target: Pareto Credit
Research rule: no vulnerability claim or testing recommendation is promoted without an explicit current scope gate.

---

## 0. Decision

The previous USDT0 plan was directionally correct but technically too narrow.

The current `reentrancy-lab` M6 module teaches a simplified cross-deployment signed-attestation failure. USDT0's current architecture is not that model. USDT0 uses LayerZero OFT/OApp components, Endpoint V2, origin/peer binding, DVN verification, Executor delivery, upgradeable EVM deployments, and a special IOTA lockbox route.

Therefore:

- M6 remains a valid **training primitive**, not a direct USDT0 detector.
- A new LayerZero-aware module is required before treating the lab as target-ready.
- USDT0 research starts from architecture + scope + audit reconciliation, not from a guessed vulnerability class.
- Pareto remains the secondary target and should reuse the improved evidence kernel, but its first research surface is vault/state/accounting rather than cross-chain messaging.
- The lab improvement program is part of the bounty track, not a separate project.

---

## 1. Epistemic state

### ESTABLISHED

- Current working lab tree contains 9 executable Solidity security modules, Slither integration, five custom detectors, bytecode-analysis documentation, and operational/OPSEC notes.
- The lab covers reentrancy, access control, oracle manipulation, vault inflation/accounting, signature replay, cross-chain domain separation, uninitialized proxy, flash-loan governance, and swap/slippage.
- The lab contains a reusable `inspector.py` and a dedicated `detect_missing_domain_binding.py`.
- USDT0 current Immunefi scope page is updated 2026-09-30 and lists 47 assets and four in-scope smart-contract impacts.
- USDT0 maximum bounty is $6M; critical direct-theft reward is 10% of directly affected mainnet funds up to $6M, with $50k minimum.
- USDT0 requires a PoC and KYC.
- USDT0 prohibits testing deployed mainnet/public-testnet code, testing with pricing oracles or third-party smart contracts, destructive/DoS activity, high-traffic automated service testing, and other Immunefi-prohibited activity.
- USDT0 documents an OFT lock-and-mint architecture with an Ethereum adapter, other-chain OFTs, LayerZero messaging, and a dedicated IOTA lockbox route.
- USDT0's current documentation states that IOTA is the Move-based IOTA L1, not IOTA EVM.
- Current USDT0 deployment documentation exposes Ethereum OAdapter and multiple transparent-upgradeable-proxy/OUpgradeable deployments.
- USDT0's public audit repository contains reports from ChainSecurity, Guardian, Paladin, OpenZeppelin, OtterSec, Zellic, and others across deployments/products.

### EXPERIMENTALLY_SUPPORTED

- The lab's own modules provide executable demonstrations for its nine modeled classes.
- The current M6 lab demonstrates that a signed message lacking deployment/domain binding can be replayed against sibling bridge deployments when they share the signer/trust root.

### INFERENCE

- M7/upgradeability analysis is directly relevant to USDT0 because current deployments use upgradeable components and proxy patterns.
- M6 concepts map to USDT0 only after being translated from raw `ecrecover`-domain separation into LayerZero's actual source/peer/origin/endpoint/message configuration model.
- M4 is a stronger first-line mapping for Pareto than for USDT0.
- M9 should become a state/invariant test around `minAmountLD` and amount conversion rather than a generic function-name scanner.

### UNKNOWN / OPEN

- Exact current code/version correspondence for every newly added USDT0 target.
- Complete audit-to-target coverage matrix for the current scope revision.
- Whether any candidate behavior, if later discovered, is already known/audited/fixed.
- Which USDT0 assets share the same implementation and which contain material per-chain deviations.
- Which LayerZero configuration states are intentionally operator-controlled versus security-critical invariants for the target.
- Whether any eventual candidate reaches one of USDT0's four in-scope impacts without relying on excluded assumptions.
- Current production prevalence of any future vulnerable state; no assumption is made here.

---

## 2. What the lab actually is

The lab is currently a **pattern-training and tool-validation environment**, not yet a target-specific auditing engine.

### Current strengths

1. Executable vulnerability fixtures rather than prose-only examples.
2. Measured exploit outputs for the included modules.
3. Stock Slither plus custom checks.
4. Explicit documentation of known tooling limitations.
5. Offline Solidity compilation workaround.
6. Proxy, signature, accounting, governance, and cross-chain examples.
7. A natural base for mutation testing and invariant testing.

### Current weaknesses that matter for bounty work

1. No real automated test suite for the lab itself. `package.json` currently declares no real test command.
2. No lockfile/pinned dependency reproducibility boundary.
3. CI inspection currently ends each inspector invocation with `|| true`; therefore inspection output is advisory rather than fail-closed.
4. Custom detectors are primarily regex/text heuristics over Slither node text.
5. The custom detector validation claim is not backed by an explicit committed positive/negative regression fixture suite.
6. `unprotected-initializer` is semantically brittle because it infers privileged variables from textual `msg.sender` comparisons instead of modeling state writes and authorization paths.
7. `unbound-signature` is too narrow for EIP-712/domain-separator patterns and can produce false reasoning when domain binding occurs outside the same function or through helper calls.
8. `raw-balance-valuation` is syntactic and does not establish whether raw balance is actually an unsafe valuation source.
9. `unbounded-swap` is function-name based and does not model whether a minimum-output invariant is enforced indirectly.
10. M3's oracle-manipulation class is intentionally not automated.
11. There is no LayerZero V2-specific fixture/module for Endpoint/Origin/Peer/Nonce/GUID/Compose semantics.
12. There is no reusable invariant/fuzz harness for cross-chain amount conservation or decimal conversion.
13. There is no target adapter that turns an Immunefi scope/deployment snapshot into an executable local-fork research target.
14. Bytecode-only analysis remains a documented gap rather than an executable pipeline.
15. Evidence packaging is not yet a first-class machine-generated artifact of each experiment.
16. There is no formal distinction in the lab CI between:
   - detector finding,
   - hypothesis,
   - reproduced invariant violation,
   - in-scope impact.

### Consequence

The next lab work must improve **measurement and semantic coverage**, not simply add more vulnerability-themed examples.

---

## 3. USDT0 current target model

USDT0 documentation currently describes these core paths:

### Path A — Ethereum → Open Mesh chain

`USDT` is locked in an Ethereum OFT Adapter.
A verified LayerZero message causes the destination OFT to mint an equivalent amount.

### Path B — Open Mesh chain → Open Mesh chain

Source OFT burns.
Destination OFT mints.
Ethereum backing does not move during this leg.

### Path C — Open Mesh chain → Ethereum

Destination-side burn produces a message that authorizes the Ethereum adapter to unlock the corresponding USDT.

### Path D — IOTA dedicated route

The Ethereum-side IOTA lockbox is a dedicated OFT Adapter.
IOTA L1 is a Move chain.
USDT0 on IOTA is paired to Ethereum through this dedicated route and is not directly connected to the other USDT0 chains.

### LayerZero security boundary

The research model must include at minimum:

`Endpoint -> Origin(srcEid, sender, nonce) -> configured peer -> receiver -> _lzReceive -> business logic`

and, where compose is present:

`_lzReceive -> sendCompose -> lzCompose -> composer`

The model must distinguish:

- EVM `chainId`
- LayerZero `eid`
- OApp/peer address
- Endpoint address
- message nonce
- GUID
- payload/message bytes
- DVN verification configuration
- Executor
- delegate/configuration authority

These are different identifiers and must not be conflated.

---

## 4. USDT0 scope gate

Current scope evidence (2026-10-06):

### Program

- Program: USDT0 / Immunefi
- Scope revision shown by Immunefi: 2026-09-30
- Assets listed by current scope page: 47
- Maximum bounty: $6,000,000
- PoC required
- KYC required

### In-scope impacts

1. Critical — direct theft of user funds, at-rest or in-motion, excluding unclaimed yield.
2. Critical — protocol insolvency.
3. Critical — permanent freezing of funds.
4. Medium — griefing.

### Important exclusions

- Incorrect third-party oracle data as the root cause.
- Basic economic/governance attacks.
- Lack of liquidity.
- Sybil/centralization-only impacts.
- Attacks requiring leaked credentials.
- Attacks relying on privileged addresses without additional privilege modification.
- Test/configuration-only impacts unless explicitly included.
- Social engineering/phishing.

### Testing boundary

All experiments must remain local/isolated under the current program rules. No mainnet/public-testnet testing. No third-party contract/oracle testing. No high-traffic automated service testing. No destructive actions.

---

## 5. USDT0 target prioritization

Do not research all 47 assets equally.

### P0 — target acquisition and correspondence

First build a current matrix:

`scope asset -> chain -> deployment address -> implementation -> proxy -> endpoint -> peer configuration -> product variant -> audit coverage`

Priority goes to assets that:
- were recently added,
- have high-value backing,
- use EVM/Solidity,
- are materially different from the already-audited canonical implementation,
- expose a unique route or configuration.

The newly added IOTA adapter is interesting because it is EVM-side and architecturally distinct; the native IOTA Move package is not a direct match for the current Solidity lab and therefore is not the first target.

### P1 — cross-chain trust and authorization

Test invariants, not signatures:

- only the expected Endpoint can trigger receive logic;
- source EID and peer pairing are correct;
- peer configuration cannot accidentally authorize a sibling/unrelated deployment;
- message origin cannot be confused with executor;
- replay protection remains valid for the actual LayerZero message model;
- nonce/GUID/path semantics do not permit duplicate economic effects;
- business logic binds all critical parameters required by its security property.

### P1 — supply and accounting conservation

For each route:

`locked + minted/burned state`

must remain consistent with the documented model.

Test:

- amountLD/amountSD conversions,
- decimal truncation/dust,
- fees,
- minAmountLD,
- send/receive accounting,
- burn-before-mint or lock/unlock correspondence,
- repeated transfer paths,
- boundary values,
- partial values near conversion boundaries.

### P1 — upgrade and initialization integrity

Model:

- proxy implementation,
- initializer state,
- admin/delegate authority,
- storage layout,
- upgrade authorization,
- implementation/proxy correspondence,
- cross-version compatibility.

### P2 — compose/callback boundary

If the target uses compose:

- validate expected sender/from,
- validate Endpoint caller,
- ensure compose messages cannot be replayed,
- ensure compose state is consumed before external effects where required,
- test whether composed execution can violate token/accounting invariants.

### P2 — configuration / DVN / Executor boundary

Configuration becomes a research object only when the configuration is itself in scope and the security impact is code-enforced.

We do not treat centralization observations or operator trust alone as reportable findings.

### P3 — legacy mesh and unusual deployment variants

Research only after the P1 surfaces are understood and the implementation differences are documented.

---

## 6. New lab work required before deep USDT0 research

### L1 — Detector correctness harness

Create committed fixtures for every custom detector:

- vulnerable positive fixture,
- fixed negative fixture,
- semantic near-miss,
- helper-function variant where applicable,
- false-positive regression.

Acceptance:

- positive detected,
- fixed detected as clean,
- near-miss clean,
- result deterministic,
- regression suite runnable offline.

### L2 — Fail-closed CI

Replace advisory inspection semantics with explicit result categories:

`PASS / FINDING / TOOL_ERROR / ENVIRONMENT_ERROR`

CI must not convert tool failure into success.

### L3 — Reproducible toolchain

Pin:

- Node version,
- Python version,
- Slither version,
- solc version,
- npm dependencies,
- Python dependencies where practical.

Record compiler/version/digest in every evidence bundle.

### L4 — Semantic custom detectors

Refactor critical detectors away from pure text heuristics.

Priority:

1. initializer/authorization dataflow;
2. signature/domain verification and helper-call resolution;
3. asset valuation/dataflow;
4. min-output enforcement;
5. proxy/implementation initialization and storage boundaries.

### L5 — LayerZero V2 module

Add a new module, not a rewrite of M6.

Required fixture families:

- valid Endpoint + valid Peer + valid Origin;
- wrong source EID;
- wrong peer;
- wrong endpoint caller;
- executor confusion;
- nonce replay;
- GUID/message mismatch;
- compose sender mismatch;
- compose Endpoint mismatch;
- ordered/unordered execution assumptions;
- amount/decimal conversion;
- fixed secure variant for every mutation.

The module should explicitly document which security property is LayerZero-enforced by the base protocol and which must be enforced by the application.

### L6 — Invariant/fuzz harness

Introduce a framework able to express properties such as:

`total_backing >= represented_supply`

`burn + mint preserves route conservation`

`received >= minAmountLD`

`a processed message cannot create a second economic effect`

`peer(srcEid) == expected_remote_oapp`

The harness should support deterministic seeds and artifact capture.

### L7 — Bytecode lane

Implement at least:

- bytecode acquisition,
- selector inventory,
- proxy detection,
- implementation resolution where possible,
- Mythril bytecode pass,
- decompiler-assisted manual review,
- source-vs-bytecode correspondence.

This closes the current BYTECODE.md gap.

### L8 — Target adapter

Create a standard target package:

`target.yaml/json`

containing:

- program
- scope revision
- asset
- chain
- address
- implementation/proxy
- source provenance
- deployment provenance
- allowed test mode
- prohibited actions
- impact classes
- known audit IDs
- experiment IDs

This becomes the bridge between the bounty monitor and the lab.

### L9 — Evidence bundle

Every completed experiment emits:

- target snapshot,
- hypothesis ID,
- invariant ID,
- exact inputs,
- environment,
- command,
- stdout/stderr,
- traces/logs,
- state deltas,
- artifact hashes,
- expected result,
- observed result,
- verdict,
- next gate.

---

## 7. Research gates

A candidate cannot progress merely because an exploit script works.

### Gate G0 — Scope

Target and action are explicitly in scope.

### Gate G1 — Version

Tested implementation corresponds to an eligible production asset/version.

### Gate G2 — Security property

There is an explicit violated invariant.

### Gate G3 — Reproduction

The violation reproduces deterministically in an isolated permitted environment.

### Gate G4 — Impact

Observed effect maps to an in-scope impact.

### Gate G5 — Preconditions

Attacker capabilities and prerequisites are permitted and realistic.

### Gate G6 — Novelty

Audit/known-issue/public-disclosure reconciliation does not already explain the result.

### Gate G7 — Minimal PoC

Counterexample is minimized without losing the security property.

### Gate G8 — Human review

No submission occurs before manual scope, impact, novelty, and evidence review.

A failure at any gate is recorded as a killed candidate, not silently discarded.

---

## 8. Kill rules

Stop early when:

- target is out of scope;
- the code path is not deployed/eligible;
- the behavior is explicitly documented as intended and no in-scope impact remains;
- the candidate requires a prohibited privileged capability;
- the invariant remains intact after adversarial perturbation;
- the apparent issue is only a linter/static warning;
- audit evidence already fully covers the same issue and it remains unfixed;
- impact cannot be mapped to the program's current impact table.

No "severity rescue" is allowed after a kill.

---

## 9. Pareto secondary track

Pareto's current Immunefi page was last updated 2026-09-24 and lists 27 assets.

The 16-September-2026 additions include Fasanara Digital, Bastion Trading, and Adaptive Frontier vault/strategy/LP-token targets. Queue contracts are explicitly out of scope. Paused and deprecated/decommissioned contracts are also excluded. Governance, Utilities, and ERC-4626 wrappers are not covered.

Current reward ceiling: $50,000.
Critical: up to $50,000.
High: up to $20,000.
Medium: up to $5,000.
PoC required.

Primary Pareto lab mapping:

- M4 → accounting/inflation/share-price research;
- M1 → callback/reentrancy where contract state permits it;
- M9 → bounded output/withdrawal/execution invariants where relevant;
- M7 → upgrade/initializer/storage boundaries if present.

Do not transfer USDT0 hypotheses into Pareto unchanged.

---

## 10. Research sequence to the current endpoint

The intended progression is:

1. Freeze USDT0 scope/deployment/audit snapshot.
2. Repair lab correctness and CI semantics.
3. Build LayerZero V2 benchmark module.
4. Validate the module against controlled mutations.
5. Build USDT0 target package for one EVM target.
6. Run static + invariant + local-fork experiments.
7. Minimize any observed counterexample.
8. Perform production correspondence.
9. Reconcile audits/known issues.
10. Run scope/impact/novelty gates.
11. Only then decide whether a finding exists.
12. Preserve all negative results.
13. Port the proven kernel to Pareto.
14. Iterate the lab from measured gaps, not from adding arbitrary vulnerability classes.

---

## 11. Explicit non-goals

This frontier does not authorize or imply:

- live mainnet probing;
- public-testnet exploitation;
- third-party protocol exploitation;
- high-volume scanning;
- privileged-role abuse;
- credential/key acquisition;
- claiming a vulnerability because a detector fires;
- treating an architectural concern as a bounty finding;
- treating a known audited issue as novel.

---

## 12. Current frontier

### Decision

Primary target: USDT0.

Primary technical gap: LayerZero-aware semantic testing.

Primary lab gap: semantic detector correctness + invariant harness + fail-closed evidence pipeline.

Secondary target: Pareto.

### Next discriminating artifacts

A. `LayerZeroV2Boundary` benchmark module.
B. Custom-detector regression suite.
C. USDT0 deployment/scope/audit matrix for one EVM target.
D. First target package with exact deployment provenance.
E. First invariant suite for supply/amount/message conservation.

### Stop condition for the USDT0 phase

The phase ends in one of three states:

- `NO_SIGNAL`: all material hypotheses killed;
- `OPEN_CANDIDATE`: reproducible but one or more external gates remain open;
- `SUBMISSION_READY`: all gates G0-G8 pass.

No other status is treated as a finding.

---

## 13. External primary sources used for this snapshot

- Immunefi — USDT0 Scope, current revision: https://immunefi.com/bug-bounty/usdt0/scope/
- Immunefi — USDT0 Information: https://immunefi.com/bug-bounty/usdt0/information/
- USDT0 Technical Documentation: https://docs.usdt0.to/
- USDT0 Developer Guide: https://docs.usdt0.to/technical-documentation/developer/
- USDT0 Deployments: https://docs.usdt0.to/technical-documentation/deployments
- USDT0 Security: https://docs.usdt0.to/technical-documentation/security
- USDT0 public audit repository: https://github.com/Everdawn-Labs/usdt0-audit-reports
- LayerZero V2 repository: https://github.com/LayerZero-Labs/LayerZero-v2
- LayerZero OFTAdapter reference: https://github.com/LayerZero-Labs/LayerZero-v2/blob/main/packages/layerzero-v2/evm/oapp/contracts/oft/OFTAdapter.sol
- LayerZero OFTCore reference: https://github.com/LayerZero-Labs/LayerZero-v2/blob/main/packages/layerzero-v2/evm/oapp/contracts/oft/OFTCore.sol
- Immunefi — Pareto Credit Scope: https://immunefi.com/bug-bounty/pareto/scope/
- Immunefi — Pareto Credit Information: https://immunefi.com/bug-bounty/pareto/information/

---

## 14. Revision rule

This document is a frontier record, not permanent truth.

Update only when evidence changes:

- target scope,
- deployment/version correspondence,
- lab capability,
- experiment result,
- audit/known-issue state,
- bounty eligibility,
- or decision gate.

Repetition without new evidence does not upgrade a claim.
