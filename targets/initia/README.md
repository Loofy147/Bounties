# Initia L1 / MoveVM — Incident Reconnaissance

**Checked:** 2026-10-25  
**Status:** RECONNAISSANCE / KNOWN PUBLIC INCIDENT  
**Bounty eligibility:** UNKNOWN / NOT VERIFIED  
**Active testing:** STOP — no current official scope, bounty terms, or post-incident target pin verified  
**Vulnerability claim:** This dossier does not claim a new vulnerability.

## Decision

Initia is a technically relevant **execution-layer research target** based on the publicly disclosed 2026-10-23 incident. It is not yet a verified bounty opportunity. The reported incident is already public, so the known root cause itself must not be treated as a novel bounty report.

Prioritize source and release provenance, official disclosure authorization, and postmortem/patch review. Do not test a live or restarted network without explicit, current authorization and a permitted environment. The public repositories checked here do not yet provide an unambiguous post-incident patch-to-deployment mapping.

## What is established

- On 2026-10-23, Initia publicly announced that its L1 and rollups were halted due to a security incident: [official Initia status post](https://x.com/initia/status/2113661738625155217).
- Initia's co-founder publicly described preliminary findings as a Day-0 MoveVM implementation issue that enabled unauthorized non-native-token minting; native INIT was stated not to be affected. Follow-up reporting attributed more specific details to Initia: a script-cache issue bypassed checks and forged VM state, assigning unbacked WETH, iUSD, and USDC balances while reported token total supply remained unchanged. [co-founder statement](https://x.com/ItsAlwaysZonny/status/2113667290059190466).
- Bitquery's on-chain investigation estimated about **$7.48M face value** of unbacked token balances and about **$2.73M of real assets** released from bridge reserves to Ethereum; it reports about **1,135.5 ETH** consolidated after swaps. These are different quantities and must not be conflated. [Bitquery investigation](https://www.bitquery.io/investigations/initia-hack).
- The bridge path matters because a counterfeit/unbacked Initia-side balance was reportedly accepted by otherwise legitimate redemption routes, releasing real reserves. This is a system-composition effect, not proof that the bridge's signature verification was itself broken.

## Current public-source pins observed

These are the public repository head commits returned by GitHub when checked on 2026-10-25. They are **source snapshots**, not proof of the exact vulnerable production binary or of any patched deployment.

| Repository | Observed main commit | Commit date | What it establishes |
|---|---|---|---|
| [initia-labs/initia](https://github.com/initia-labs/initia/commit/4fbd602e218b4e902d2c62bedd5d7b1263db47d6) | `4fbd602e218b4e902d2c62bedd5d7b1263db47d6` | 2026-09-29 | Public L1 source head predates the incident |
| [initia-labs/movevm](https://github.com/initia-labs/movevm/commit/a15fe49d492f5369dff63e29722334815e833bcc) | `a15fe49d492f5369dff63e29722334815e833bcc` | 2026-05-28 | Public MoveVM binding/runtime source head predates the incident |
| [initia-labs/move](https://github.com/initia-labs/move/commit/d8d413038acd7202152a55d8c5c2441621ad53c8) | `d8d413038acd7202152a55d8c5c2441621ad53c8` | 2025-11-20 | Public Move fork head observed; not a production patch pin |

The Move fork's [SECURITY.md](https://github.com/initia-labs/move/blob/main/SECURITY.md) points to the **Aptos Foundation** bounty program. That does not establish that the Aptos program covers Initia's fork, L1 binary, or incident. No Initia-specific public bounty terms were verified in this review. The current [Immunefi program catalog](https://immunefi.com/bug-bounty/) was checked; no Initia program page was found in the sources reviewed. This is a search result, not proof that no private or separately hosted disclosure program exists.

## Status labels

- **ESTABLISHED:** The incident and network halt were publicly acknowledged by Initia; the high-level MoveVM attribution and unaffected native INIT statement were publicly attributed to Initia; on-chain analysis reports reserve releases.
- **EXPERIMENTALLY_SUPPORTED:** No experiment was run as part of this dossier.
- **INFERENCE:** This is a good fit for execution-layer state integrity, cache isolation, asset-accounting invariants, and cross-domain redemption consistency.
- **HYPOTHESIS:** A regression suite may uncover additional defects in a released patch or adjacent, distinct code paths. No candidate is currently demonstrated.
- **UNKNOWN:** Exact root-cause code path, vulnerable commit/build, patch commit and deployed version, full postmortem, current network status after the cited halt, external bounty existence and terms, permission for third-party testing, report deadline, KYC/payout conditions, and known-issue rules.

## Hard gates before any testing

1. Obtain an official postmortem and immutable patch/source references.
2. Map the source commit and MoveVM native library/build artifacts to the affected Initia release and then to the fixed release. Version strings alone are insufficient.
3. Verify an Initia-specific program or written authorization: exact assets, allowed local/test environment, disclosure channel, rewards, eligibility/KYC, PoC format, known-issue exclusions, and reporting deadline.
4. Do not submit the public incident itself as a novel discovery. Any future candidate must be a distinct, newly evidenced issue, with its initial-discovery time recorded.
5. Only after the above gates, perform bounded local regression tests and independently validate results.

## Candidate areas — hypotheses only

Use [RESEARCH-PLAN.md](RESEARCH-PLAN.md) for the non-exploitative plan and [the invariant-monitor specification](../../research/INITIA-ASSET-STATE-INVARIANTS-v0.1.md) for proposed detection properties. Candidate areas are not claims that any current code fails them.

- Script-cache / verification-context consistency.
- Balance-state mutation authorization and per-asset accounting reconciliation.
- Cross-domain backing, burn, and reserve-release correspondence.
- Transaction/session isolation and state-cache lifecycle.

## Scope boundary

Do not test the halted chain, its public endpoints, production bridges, or user assets. Do not recreate the known exploit against a live service. Use public-source review and safe specification work only until official terms and a permitted test setup are confirmed.
