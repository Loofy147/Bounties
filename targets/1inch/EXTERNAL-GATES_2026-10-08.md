# 1inch B0 — External Gate Update

Snapshot: 2026-10-08
Research line: 1inch Limit Order Protocol 4.3.4
Target commit: 7da29889efa2e635611e1caf60f85f595ff7f05f
Working branch: research/b0-1inch-external-gates-2026-10-08

## Purpose

Record the external evidence work performed after the 2026-09-29 H-E2 research endpoint.

The technical local reproduction is not being extended. The remaining work is evidence reconciliation, production-state characterization, and eligibility closure.

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

## Gate 2 — H-E2 source semantics

Status: ESTABLISHED at source level

The tagged 4.3.4 NativeOrderImpl source was inspected directly.

The resolver cancellation path:

- is gated by a non-zero balance of the configured access token for msg.sender;
- requires the maker order to be expired;
- when rewardLimit > 0, requires the configured cancellation delay and computes resolverReward from block.basefee and the 70,000 gas lower bound;
- calls _cancelOrder(makerOrder, resolverReward);
- _cancelOrder first reads the clone's full WETH balance;
- it withdraws that full balance;
- it subtracts resolverReward from that balance;
- it pays the resolver the reward;
- it sends the remainder to the maker.

This is the implementation basis for H-E2. It is not a claim that the behavior is a security vulnerability.

Primary target source:
https://github.com/1inch/limit-order-protocol/blob/4.3.4/contracts/extensions/NativeOrderImpl.sol

## Gate 3 — audit coverage

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

## Gate 4 — current bounty scope / role eligibility

Status: NARROWED, NOT CLOSED

Current 1inch Smart Contracts Immunefi rules state:

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

## Gate 5 — real production residual-state evidence

Status: PARTIALLY ESTABLISHED; prevalence UNKNOWN

A concrete public-chain NativeOrder clone provides a useful production state-transition example:

Clone:
0xb3eea3d5e2ef2728e40f9783fc781bf21f2de58f

Creation / funding:
- block 25365981
- factory transferred 4,000,000,000,000,000,000 wei to the clone
- the clone deposited the same 4 ETH-equivalent amount into WETH

Subsequent WETH transfers out of the clone:
- block 25365982: 2.0 WETH
- block 25366000: 0.2 WETH
- block 25366001: 0.45 WETH

These three transfers total 2.65 WETH.

Resolver cancellation:
- transaction 0x9d6db312e6e58187b8f3c9da6e78c2a9545230b2b94413570db209a6e1a136a1
- block 25366005
- NativeOrderCancelledByResolver event reports balance = 1.35 ETH-equivalent
- resolverReward = 0

Accounting reconciles exactly:

4.00 - 2.00 - 0.20 - 0.45 = 1.35 ETH

This is strong evidence that an ordinary production native order can have a residual clone balance after multiple outbound WETH transfers before resolver cancellation.

Because the public transfer records were not decoded into the full order-fill call graph, record the state as production residual/partial-fill evidence rather than as a complete transaction-level proof of the exact order-fill semantic.

Prevalence is not quantified.

No production contract was tested or modified.

## Gate 6 — search for production resolver rewards

Status: OBSERVED NO POSITIVE SAMPLE IN CHECKED WINDOW

A passive Etherscan log search for NativeOrderCancelledByResolver events over blocks 24,000,000–26,000,000 returned 5,272 events across six populated pages.

Within that checked window, every decoded event returned resolverReward = 0.

This does not invalidate the H-E2 model because the modeled condition concerns a resolver cancellation with rewardLimit > 0 and a residual balance below the computed reward. It does, however, mean that the current passive production sample does not yet demonstrate a real on-chain instance of a non-zero resolver reward.

## Current H-E2 state

Technical local behavior: EXPERIMENTALLY_SUPPORTED

Source semantics: ESTABLISHED

Natural production residual state: PARTIALLY_ESTABLISHED

Production non-zero resolver-reward occurrence: UNKNOWN / no positive sample in checked window

Audit/known-issue eligibility: OPEN

Resolver-role eligibility: OPEN

Overall bounty finding: HYPOTHESIS

No severity, payout, or submission decision is assigned.

## Decision

STOP NEW SYNTHETIC H-E2 VARIANTS.

The remaining discriminating work is external to the existing local reproduction:

1. reconcile the complete applicable audit / known-issue history;
2. settle resolver-role treatment under the current program rules;
3. continue passive production analysis only far enough to determine whether a non-zero resolver reward with a naturally low residual balance occurs in real usage.

Do not test the deployed production contract or public networks for exploit reproduction. All executable validation remains on permitted local forks.

## Evidence references

1. 1inch Limit Order Protocol 4.3.4 target source:
https://github.com/1inch/limit-order-protocol/tree/4.3.4

2. NativeOrderImpl 4.3.4:
https://github.com/1inch/limit-order-protocol/blob/4.3.4/contracts/extensions/NativeOrderImpl.sol

3. 1inch audit archive:
https://github.com/1inch/1inch-audits

4. 1inch Smart Contracts Immunefi scope:
https://immunefi.com/bug-bounty/1inch-SmartContracts/scope/

5. 1inch Smart Contracts Immunefi information:
https://immunefi.com/bug-bounty/1inch-SmartContracts/information/

6. Verified NativeOrderFactory address:
https://etherscan.io/address/0xe12e0f117d23a5ccc57f8935cd8c4e80cd91ff01

7. Example production resolver-cancellation transaction:
https://etherscan.io/tx/0x9d6db312e6e58187b8f3c9da6e78c2a9545230b2b94413570db209a6e1a136a1
