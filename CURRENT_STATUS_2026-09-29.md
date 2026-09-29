# Bounty Track Current Status — 2026-09-29

**Repository:** `Loofy147/Bounties`

## Target

Current B0 target: **1inch Smart Contracts / Limit Order Protocol**.

Working production line:
- tag `4.3.4`
- commit `7da29889efa2e635611e1caf60f85f595ff7f05f`

The current Immunefi program lists Limit Order Protocol in scope, requires a PoC, applies to the latest eligible tags/releases, and permits local-fork testing rather than testing deployed mainnet/public-testnet code. citeturn314897view0

## Execution frontier

Research branch:
`bounty/research-4.3.4`

Run #32:
- GitHub Actions: `36522991905`
- research head: `75f8dfde597a408e28d6e633dad6ea9c805833bc`
- result: **SUCCESS**

Four independent controls passed:
- NativeOrder ERC-1271 boundary — 1 passing
- NativeOrder clone isolation — 1 passing
- resolver reward total-balance control — 1 passing
- undercollateralized resolver reward control — 1 passing

Therefore H-E2 execution is now **EXPERIMENTALLY_SUPPORTED**.

The reproduced undercollateralized case uses:
- maker collateral (C=0.0001) ETH;
- 10 gwei base fee;
- resolver reward cap (R=0.00077) ETH;
- resolver WETH top-up (R-C=0.00067) ETH;
- cancellation after expiry plus the configured delay.

The test observes zero maker balance delta from the cancellation and resolver proceeds equal to the full reward after gas cost is added back.

## Resolver adversary model

**ESTABLISHED:** resolver is a permissioned operational actor and the intended caller of resolver cancellation.

1inch's resolver material says resolvers must register/pass verification and that an Access NFT functions as an access credential for exclusive order-fulfillment functionality. citeturn595204search5turn595204search8

**OPEN / INFERENCE:** the current 1inch bounty text excludes attacks requiring privileged addresses and names governance and strategist as examples, but does not expressly classify resolver/access-token-holder roles. citeturn314897view0

Consequently, the technical adversary model includes the resolver, while bounty eligibility remains unresolved.

## Design-intent evidence

Upstream `1inch/limit-order-protocol` PR #390 contains an explicit review exchange about returning the **whole WETH balance** to the maker, including accidentally deposited WETH. The maintainer stated that this behavior was intended. The same implementation subtracts resolver reward from that full balance.

This is strong evidence that full-balance semantics were consciously designed, but it does not prove that the resolver interaction was previously recognized.

## Audit / known-issue gate

The official 1inch audit archive contains a v4.3.4 OpenZeppelin report file. citeturn812425view0

The archive material available to this research identifies that v4.3.4 entry as the Permit2Proxy extension; current evidence therefore does not establish NativeOrderFactory/NativeOrderImpl coverage by that particular audit. This is not evidence that NativeOrder was never reviewed elsewhere.

Targeted GitHub searches over the current Limit Order Protocol repository found the resolver-cancellation implementation and tests, but no explicit prior source-text hit for the reproduced undercollateralized condition.

That absence is **not a novelty proof**. Audit/known-issue reconciliation remains an open gate.

## Current status

B0-1INCH overall: **HYPOTHESIS**

H-E2 local behavior: **EXPERIMENTALLY_SUPPORTED**

Bounty eligibility: **OPEN**

No severity, bounty amount, or submission decision is assigned.

Next gate:
`resolver eligibility → audit/known-issue reconciliation → minimum victim-impact characterization → submission eligibility`
