# 1inch B0 — External Gate Update

Snapshot: 2026-10-08
Research line: 1inch Limit Order Protocol 4.3.4
Target commit: 7da29889efa2e635611e1caf60f85f595ff7f05f
Working branch: research/b0-1inch-external-gates-2026-10-08

## Purpose

Record the external evidence work performed after the 2026-09-29 H-E2 research endpoint.

The technical local reproduction is not being extended. The remaining work is evidence reconciliation and eligibility closure.

## Gate 1 — production deployment/source correspondence

Status: ESTABLISHED

Official deployment correspondence recorded by the research track identifies:

- NativeOrderFactory: 0xe12E0f117d23a5ccc57f8935CD8c4E80cD91FF01

Current verified Etherscan source for that address identifies:

- Contract: NativeOrderFactory
- Contract file: contracts/extensions/NativeOrderFactory.sol
- Compiler: v0.8.30+commit.73712a01
- EVM version: shanghai
- optimizer: enabled, 1,000,000 runs

A normalized source comparison was performed between:

- 1inch/limit-order-protocol, tag 4.3.4, contracts/extensions/NativeOrderFactory.sol
- the verified Etherscan source for 0xe12e...FF01

Result: exact_source_match = true.

This establishes source-level correspondence for the researched NativeOrderFactory implementation at the recorded production address.

It does not establish production prevalence of the H-E2 state.

## Gate 2 — audit coverage

Status: OPEN

The official 1inch audit archive contains a dedicated folder:

Limit Order Protocol v4.3.4

Its description identifies the review as:

"The Permit2Proxy extension for the Limit Order Protocol — a simpler Permit2 integration without witness data, used to transfer maker and taker assets via Permit2 signature transfers."

The archive also contains older Limit Order Protocol audit material and a separate Aggregation Protocol v6 / Limit Order Protocol v4 section.

Current evidence therefore supports:

- v4.3.4 has an OpenZeppelin report;
- the dedicated v4.3.4 report is described as a Permit2Proxy review;
- this report alone does not establish NativeOrderFactory / NativeOrderImpl coverage.

Do not infer that NativeOrder was never audited elsewhere. Full audit/known-issue reconciliation remains OPEN.

Primary archive:
https://github.com/1inch/1inch-audits

## Gate 3 — current bounty scope / role eligibility

Status: NARROWED, NOT CLOSED

Current 1inch Smart Contracts Immunefi scope states:

- only the latest eligible tags/releases apply;
- PoC is required;
- Critical smart-contract reward is 10% of directly affected funds, capped at $500,000, with a $30,000 minimum;
- impacts caused by attacks requiring privileged addresses are out of scope where the privileged addresses are governance or strategist, except where the contracts are intended to have no privileged access to the affected functions.

The researched H-E2 mechanism uses the resolver cancellation path and requires the resolver access token.

The current published rule names governance and strategist but does not expressly name resolver in that exclusion.

This narrows the role-eligibility question but does not, by itself, establish that a resolver-triggered scenario is bounty-eligible. The final decision must remain with the program rules/triage.

Primary scope:
https://immunefi.com/bug-bounty/1inch-SmartContracts/scope/

Primary information page:
https://immunefi.com/bug-bounty/1inch-SmartContracts/information/

## Gate 4 — production victim-state prevalence

Status: OPEN

Passive production evidence establishes that NativeOrderFactory is deployed and has emitted NativeOrderCreated events.

Public-chain evidence also shows resolver-cancellation activity for NativeOrder clones.

What is not yet established is the minimum production population of ordinary partial-fill states that leave residual clone WETH below the resolver reward amount before resolver cancellation.

This gate is an evidence question only. No production testing is authorized or implied.

## Current H-E2 state

Technical local behavior: EXPERIMENTALLY_SUPPORTED

Overall bounty finding: HYPOTHESIS

No severity, payout, or submission decision is assigned.

## Decision

STOP NEW SYNTHETIC H-E2 VARIANTS.

The next discriminating work should be limited to:

1. audit/known-issue reconciliation against the complete applicable archive;
2. formal role-eligibility reading against current Immunefi rules;
3. passive production-state evidence sufficient to establish whether the modeled residual state occurs in real usage.

Do not test the deployed production contract or public networks for exploit reproduction. All executable validation remains on permitted local forks.

## Evidence references

1. 1inch Limit Order Protocol 4.3.4 target source:
https://github.com/1inch/limit-order-protocol/tree/4.3.4

2. 1inch audit archive:
https://github.com/1inch/1inch-audits

3. 1inch Smart Contracts Immunefi scope:
https://immunefi.com/bug-bounty/1inch-SmartContracts/scope/

4. 1inch Smart Contracts Immunefi information:
https://immunefi.com/bug-bounty/1inch-SmartContracts/information/

5. Verified NativeOrderFactory address:
https://etherscan.io/address/0xe12e0f117d23a5ccc57f8935cd8c4e80cd91ff01
