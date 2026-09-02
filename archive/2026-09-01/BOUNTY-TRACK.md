# Bounty Track — Live Target Snapshot

**Snapshot date:** 2026-09-01

This file is the operational companion to `docs/PROTOCOL-VERIFICATION-ROADMAP.md`. It records candidate paid targets for the parallel bounty track. Availability, scope, eligibility, reward rules, and exclusions can change; verify the live program page immediately before submitting anything.

## Objective

The first target is not selected by reward size. The immediate milestone is the first legitimate, in-scope, externally accepted paid finding — even if the payout is small.

The working loop is:

```text
scope → inspect → hypothesize → reproduce → minimize → document → submit → triage → acceptance → payment
```

## B0 — first paid finding

**Primary reconnaissance target: 1inch Smart Contracts.**

The program is currently live, requires a PoC and KYC for payout, and lists a low-severity reward starting at $100. Its in-scope assets include Limit Order Protocol, Limit Order Settlement, Token-plugins, Farming Contracts, Delegating Contracts, Cross-chain Swap, Solana Crosschain and Solana Fusion. The program applies only to the latest tags/releases. Testing must be performed on local forks; mainnet/public-testnet testing and several categories of speculative or out-of-scope activity are prohibited. Reports are expected within 24 hours of discovery. Do not begin active testing until the exact current release, asset and impact category are pinned locally.

B0 is not selected because the reward is large. It is selected because it gives us a concrete, paid, PoC-based external feedback loop with a published low-tier floor.

## Current candidate set

| Priority | Program | Technical fit | Current public maximum | Why it matters | Immediate action |
|---|---|---:|---:|---|---|
| B0 | 1inch Smart Contracts | Medium | $500,000 | Concrete low-tier paid path; strict scope; latest releases; PoC required | Pin latest release, read audits/known issues, build local-only test environment |
| A | Cosmos | Very high | $50,000 | Explicitly covers distributed-systems protocols, consensus, interoperability and infrastructure; Go/Rust/C/C++/CosmWasm | Study scope + known issues before any testing |
| A- | The Graph | High | $50,000 | Decentralized indexing protocol; Go/Rust infrastructure; deterministic/inconsistent query-result impacts are explicitly relevant | Review Graph Node/Indexer scope and prior audits |
| B | Berachain | High | $100,000 | BeaconKit consensus-client stack plus Rust execution client; L1 protocol impacts | Build protocol map before touching code |
| B | Sei | High | $500,000 | L1; Go/Rust; consensus/chain infrastructure | Treat as a later, harder target |
| B | sBTC | High | $250,000 | Stacks/Bitcoin infrastructure with Rust signer and supporting libraries | Requires deeper Bitcoin/bridge understanding |
| C | Chainlink | Medium–high | $3,000,000 | Large Go/Rust protocol/infrastructure scope, but broader domain and higher complexity | Use as a later-stage target |

## B0 readiness gate

Do not submit or perform live testing until all of the following are satisfied:

- exact in-scope repository, tag/release and contract are pinned;
- the claimed impact appears verbatim in the current scope;
- relevant known issues and released audit findings have been checked;
- all experiments run locally or on an explicitly permitted fork;
- a minimal deterministic PoC demonstrates the impact without modifying real user data or production state;
- the report can be written from observed evidence rather than speculation;
- the reporting deadline and platform submission channel are known.

## Selection rule

Before spending more than a short reconnaissance session on a target, record:

1. exact asset/version in scope;
2. exact impact category required for payment;
3. known issues and prior audit exclusions;
4. reproducibility path;
5. required PoC format;
6. eligibility/KYC constraints;
7. expected time to a falsifiable result.

Stop quickly when the target does not produce a credible signal.

## Relationship to Moirae

Moirae trains the transferable reasoning pattern:

```text
protocol specification
→ state machine
→ invariants
→ adversarial schedule
→ deterministic trace
→ minimized counterexample
→ evidence
```

A bounty target is the external transfer test of that method.

## Non-goals

Do not optimize for the largest advertised payout. Do not submit speculative reports. Do not test assets that are out of scope. Do not use AI-generated claims without deterministic reproduction.

## Source links

- 1inch Smart Contracts: https://immunefi.com/bug-bounty/1inch-SmartContracts/information/
- 1inch Smart Contracts scope: https://immunefi.com/bug-bounty/1inch-SmartContracts/scope/
- Cosmos: https://immunefi.com/bug-bounty/cosmos/information/
- Cosmos resources: https://immunefi.com/bug-bounty/cosmos/resources/
- The Graph: https://immunefi.com/bug-bounty/thegraph/information/
- Berachain: https://immunefi.com/bug-bounty/berachain/information/
- Berachain scope: https://immunefi.com/bug-bounty/berachain/scope/
- Sei: https://immunefi.com/bug-bounty/sei/scope/
- sBTC: https://immunefi.com/bug-bounty/sbtc/scope/
- Chainlink: https://immunefi.com/bug-bounty/chainlink/information/
