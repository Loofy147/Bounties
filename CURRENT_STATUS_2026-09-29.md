
# Bounty Track Current Status — 2026-09-29

Repository: Loofy147/Bounties

## Target

Current B0 target: 1inch Smart Contracts / Limit Order Protocol.

Production line under research:
- tag 4.3.4
- commit 7da29889efa2e635611e1caf60f85f595ff7f05f

The current Immunefi program lists Limit Order Protocol in scope, requires a PoC, and applies to the latest eligible tags/releases. The program also documents local-fork testing rules rather than testing deployed mainnet/public-testnet code. [Current external scope verified 2026-09-29.]

## Execution frontier

Research branch:
bounty/research-4.3.4

Current PR:
- #1
- open, unmerged, research-only
- current head: 8b59d02804de118ac9bd5ee2f18e58a2d5cf8a38

Latest complete boundary-suite run:
- GitHub Actions run #64
- id 36621806098
- job 109588790780
- head 8b59d02804de118ac9bd5ee2f18e58a2d5cf8a38
- result: SUCCESS — all six controls passed.

Passed before the final defect:
- target pin PASS
- package version 4.3.4 PASS
- NativeOrder ERC-1271 boundary PASS
- same-maker clone isolation PASS
- resolver reward total-balance control PASS
- undercollateralized resolver reward control PASS
- economic victim-loss calibration PASS

The dedicated partial-fill harness then exposed two additional harness defects before the final run:
- an absolute maker DAI balance assertion was used after the fixture pre-funded the maker;
- the computed expiration timestamp was not encoded into makerTraits, so cancellation correctly reverted with OrderShouldBeExpired.

These were harness defects, not contract failures. The final corrected head is 8b59d02804de118ac9bd5ee2f18e58a2d5cf8a38.

## H-E2 technical behavior

H-E2 local behavior remains EXPERIMENTALLY_SUPPORTED.

The resolver cancellation implementation:
- requires the resolver access token;
- requires order expiry plus cancellation delay when rewardLimit > 0;
- computes a reward from basefee and the 70,000 gas lower bound;
- reads the clone's full WETH balance;
- unwraps that balance;
- pays the resolver reward from that aggregate balance;
- sends only the remainder to the maker.

For C < R, a resolver can locally provide T = R-C, making total clone balance R and leaving zero maker proceeds from cancellation.

## Victim-impact calibration

Successful economic calibration on run #51:

- maker residual C = 0.0007 ETH
- reward cap R = 0.00077 ETH
- resolver top-up T = 0.00007 ETH
- cancellation gas used = 56,627
- effective gas price = 11 gwei
- cancellation gas cost = 0.000622897 ETH
- maker-side cancellation loss = 0.0007 ETH
- resolver reward = 0.00077 ETH

This proves the victim-side loss measurement and the reward transfer at the selected local parameters.

The complete partial-fill run also characterized end-to-end resolver economics.

## Natural victim state

The upstream 4.3.4 test suite contains a native ETH-maker partial-fill case:
- 0.3 ETH-equivalent initial WETH collateral;
- 0.2 partial fill;
- 0.1 WETH remains in the clone;
- maker cancellation refunds the residual.

Therefore a residual clone balance below the initial order amount is a normal protocol state.

Our dedicated partial-fill control reproduced the same state transition and then successfully executed resolver cancellation after expiry plus delay.

## Resolver adversary model

ESTABLISHED:
resolver is a permissioned operational actor and intended caller of resolver cancellation.

OPEN / INFERENCE:
the current bounty scope excludes attacks requiring privileged addresses and names governance and strategist as examples, but does not expressly classify resolver/access-token-holder roles.

Bounty eligibility remains OPEN for final production, audit/known-issue, and program-rule reconciliation.

## Design-intent / known-issue evidence

Upstream PR #390 explicitly discussed returning the whole WETH balance to the maker, including accidentally deposited WETH. The maintainer stated that full-balance behavior was intentional.

Targeted GitHub searches found no explicit prior disclosure of the tested undercollateralized reward condition.

Neither point is novelty proof. Full audit/known-issue reconciliation remains OPEN.

## Audit gate

The official audit archive contains a v4.3.4 OpenZeppelin report entry. Current archive evidence associates that entry with the Permit2Proxy extension, so present evidence does not establish NativeOrderFactory/NativeOrderImpl coverage by that particular report.

Do not infer that NativeOrder was never audited.

## Current status

B0-1INCH overall: HYPOTHESIS

H-E2 local behavior: EXPERIMENTALLY_SUPPORTED

K-04 undercollateralized resolver reward extraction: REOPENED; the earlier profitability-only kill is retired.

Bounty eligibility: OPEN.

No severity, bounty amount, or submission decision has been assigned.

Final remaining gates:
reconcile applicable audits/known issues → settle resolver-role treatment under the program's privileged-address rule → establish production deployment/version correspondence and minimum real victim state. Do not submit before those gates are closed.
