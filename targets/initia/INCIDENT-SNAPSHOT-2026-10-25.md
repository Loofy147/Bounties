# Initia MoveVM Incident — Source and Evidence Snapshot

**Observation cutoff:** 2026-10-25  
**Classification:** RECONNAISSANCE / already-public incident  
**Evidence policy:** Primary statements, repository metadata, and independent chain analysis remain separate.

## Timeline

- **2026-10-23:** Initia announced that L1 and rollups were halted at 15:41:30 UTC due to a security incident: [official Initia status post](https://x.com/initia/status/2113661738625155217).
- **2026-10-23:** Initia's co-founder described preliminary findings as a previously unknown MoveVM issue allowing unauthorized token minting/assignment while not affecting native INIT: [statement](https://x.com/ItsAlwaysZonny/status/2113667290059190466).
- **2026-10-23:** Bitquery recorded a face-value total of about $7.48M in unbacked balances, about $2.73M in actual reserve releases, and about 1,135.5 ETH consolidated on Ethereum in the period it observed: [on-chain investigation](https://www.bitquery.io/investigations/initia-hack).

This report preserves the incident-time snapshot. It does not claim the wallet status or network halt status remains unchanged after the source observation.

## Keep these quantities separate

| Quantity | Reported value | Evidence type | Meaning |
|---|---:|---|---|
| Unbacked balances created at face value | ~$7.48M | Bitquery chain investigation | Not equal to cashable value |
| Real assets released from bridge reserves | ~$2.73M | Initia-attributed statement and chain tracing | Better measure of actual external extraction |
| Consolidated proceeds | ~1,135.5 ETH | Bitquery chain tracing | Post-swap aggregate as observed |
| Native INIT minted | None reported | Initia-attributed statement | Native INIT was reported unaffected |
| Token total supply counters | Reported unchanged | Initia-attributed statement | Suggests account/state corruption rather than an ordinary authorized supply increase; precise semantics require code-level confirmation |

Reported assets include WETH/ETH, AUSD0 (the Initia-side representation of AUSD), USDC, and iUSD. Labels differ by stage: unbacked Initia-side balances, bridge messages/redemptions, and external reserve assets are not interchangeable names for one token.

## Public source snapshots

GitHub branch refs were checked on 2026-10-25.

- [Initia L1 main head](https://github.com/initia-labs/initia/commit/4fbd602e218b4e902d2c62bedd5d7b1263db47d6) — commit dated 2026-09-29.
- [MoveVM main head](https://github.com/initia-labs/movevm/commit/a15fe49d492f5369dff63e29722334815e833bcc) — commit dated 2026-05-28.
- [Move fork main head](https://github.com/initia-labs/move/commit/d8d413038acd7202152a55d8c5c2441621ad53c8) — commit dated 2025-11-20.
- [Move fork SECURITY.md](https://github.com/initia-labs/move/blob/main/SECURITY.md) names the Aptos Foundation bounty program, not an Initia-specific program.

No public post-incident patch or production binary pin was established from these repository heads. This means **patch provenance is UNKNOWN**, not that the incident remains exploitable or that no private patch exists.

## No bounty eligibility established

Checked sources:
- [Initia official website](https://initia.xyz/)
- [Initia L1 repository](https://github.com/initia-labs/initia)
- [Initia MoveVM repository](https://github.com/initia-labs/movevm)
- [Initia Move fork](https://github.com/initia-labs/move)
- [Immunefi's program catalog](https://immunefi.com/bug-bounty/)

No Initia-specific public terms were found in this review. No reward, scope, KYC, initial-discovery deadline, PoC rule, testing policy, or known-issue exclusion is inferred. The already-public incident is known and must not be reported as a novel discovery. Reconcile program eligibility before any future disclosure or testing.

## Evidence labels

- **ESTABLISHED:** Publicly attributed incident details and the listed source-head metadata.
- **EXPERIMENTALLY_SUPPORTED:** Nothing new was executed.
- **INFERENCE:** State-integrity and cache-context properties are relevant review families.
- **HYPOTHESIS:** Future regression or adjacent-code findings may exist after a verified patch becomes available.
- **UNKNOWN:** Exact bug mechanism, changed files, patch, deployed build identity, scope/reward terms, and permission to test.
