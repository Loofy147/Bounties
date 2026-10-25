# stUSDS Keeper / Rate Setter — Authorization Boundary Review

Date: 2026-10-25
Status: HYPOTHESIS KILLED FOR THE CURRENT LIVE AUTOMATION PATH — the keeper remains authorized, but the on-chain submission switch is 0 at pinned block 26,267,715. Monitor for reactivation; do not submit.
Target: Sky / Maker stUSDS, Ethereum mainnet
Primary sources:
- https://github.com/sky-ecosystem/stusds/blob/master/src/StUsdsRateSetter.sol
- https://github.com/sky-ecosystem/stusds/blob/master/README.md
- https://github.com/sky-ecosystem/spells-mainnet/blob/0cdb284be3772f9686f0605610565faf130b76ef/archive/2026-10-08-DssSpell/DssSpell.sol
- https://github.com/sky-ecosystem/spells-mainnet/blob/0cdb284be3772f9686f0605610565faf130b76ef/archive/2026-10-08-DssSpell/DssSpell.t.sol

## Claim ledger

- ESTABLISHED — `StUsdsRateSetter.set(strBps, dutyBps, line, cap)` is callable only by an address with `buds[msg.sender] == 1`, and only while `bad == 0` and after the cooldown.
- ESTABLISHED — `set()` constrains `strBps` and `dutyBps` to configured min/max and per-update step; `line` and `cap` are bounded by `maxLine` and `maxCap`.
- ESTABLISHED — the setter does not directly query utilization or enforce a utilization-dependent precondition in `set()`.
- ESTABLISHED — the stUSDS README assigns resistance to manipulation attempts to the off-chain operator algorithm, noting that it may use average historical utilization and varied samples.
- ESTABLISHED — the 2026-10-08 executive spell source calls `kiss(0x068F9c8F33E13c18B852877A5D8Ec61504971376)` on the Chainlog-resolved `STUSDS_RATE_SETTER`, and lowers both the STR and duty step parameters from 1,500 bps to 500 bps.
- ESTABLISHED — at Ethereum block `26,267,715` (`0x190d043`, timestamp `2026-10-25T05:51:59Z`), the current Chainlog points to rate setter `0x30784615252B13E1DbE2bDf598627eaC297Bf4C5` and ValueRegistry `0xcDb55A799A9B9eAe22Ed0E13037bb6D2E3f1d080`. Direct reads return `buds(keeper)=1`, `bad=0`, `tau=57,600`, `toc=2026-10-15T15:23:11Z`, `maxLine=1,000,000,000 USDS`, `maxCap=1,000,000,000 USDS`, `strCfg=(200,5000,500)` bps, and `dutyCfg=(210,5000,500)` bps.
- ESTABLISHED — `eth_getCode(0x068F9c8F33E13c18B852877A5D8Ec61504971376)` returns `0x`: the authorized keeper address is an EOA, not a contract exposing a publicly callable execution path. The official Atlas says the interest-rate-model algorithm is not publicly disclosed. UNKNOWN — private keeper implementation, run-time inputs, and internal trigger/decision logic.
- CONTRADICTED (current live automation) — the ValueRegistry returns `STUSDS_KEEPER_ENABLED=0`, so its documented behavior is calculate/record without submitting. No keeper-originated `set()` execution was identified in the inspected event window.
- NOT ESTABLISHED — no attacker-controlled route, profitable state transition, insolvency, theft, or bounty-eligible impact has been demonstrated.

## Live-chain recheck (2026-10-25)

Pinned block: `26,267,715` / `0x190d043`; timestamp `2026-10-25T05:51:59Z`. Calls were read-only and pinned to that block.

### ValueRegistry parameters observed on-chain

The following values were returned by `getValue(bytes32)` from the current Chainlog-listed ValueRegistry:

| Key | Value |
|---|---:|
| `STUSDS_OPT_UTIL_WAD` | 0.90 |
| `STUSDS_DISTRIBUTION_REWARD_WAD` | 0.002 |
| `STUSDS_BASE_SPREAD_WAD` | 0.001 |
| `STUSDS_SPREAD_PCT_WAD` | 0.10 |
| `STUSDS_TIME_DRIFT_SPEED_WAD` | 0.03 |
| `STUSDS_ABOVE_KINK_MULT_WAD` | 0.77 |
| `STUSDS_AVG_UTILIZATION_HOURS` | 24 |
| `STUSDS_CAP_FACTOR_WAD` | 1.35 |
| `STUSDS_LINE_FACTOR_WAD` | 1.20 |
| `STUSDS_UPDATE_THRESHOLD_BPS` | 2 |
| `STUSDS_KEEPER_RERUN_SECONDS` | 1,200 (20 minutes) |
| `STUSDS_KEEPER_ENABLED` | **0** |

WAD values above are normalized by (10^{18}). The official Atlas specifies that a zero `STUSDS_KEEPER_ENABLED` means the Keeper may calculate and record recommended values but does not submit the rate-setter transaction.

### Event and transaction trace

- `STUSDS_KEEPER_ENABLED=0` was written on `2026-10-07T14:23:11Z`, transaction `0x42a48f08942f14d3e4b1a8baa378fe8a37798a7892b6a46a2fb00673cc535c12`. The current read is still zero; no subsequent write changing this key to one appeared in the inspected log range.
- The keeper's `Kiss` event occurred on `2026-10-12T14:01:47Z`, transaction `0x93389082b75a9e278b6b2a2d7dde53618c38214b5d71699fd60461dbe1e10275`. That proves authorization, not activation.
- Four `Set(uint256,uint256,uint256,uint256)` events were observed between `2026-10-09T23:20:23Z` and `2026-10-15T15:23:11Z`, at blocks `0x18f2416`, `0x18f3721`, `0x18f8db3`, and `0x18fc303`. Each corresponding transaction was executed through the documented Operator Multisig `0xBB865F94B8A92E57f79fCc89Dfd4dcf0D3fDEA16`, not directly by the keeper EOA. No further `Set` event appeared through pinned block `26,267,715` in the inspected log query.
- The documented Operator Multisig is a 2-of-3 Safe controlled by Core GovOps. Its use for these updates is consistent with the protocol's documented manual-update pathway.

### Interpretation

This is evidence against an *active automated keeper exploit path*, not proof that every aspect of stUSDS is safe. The rate setter has no utilization-aware precondition, but its caller must already possess `buds` authority; the only observed updates in the inspected window were submitted through the operator multisig. The keeper EOA has no contract bytecode, and an unprivileged caller cannot impersonate it at the `toll` check without compromising or controlling that key.

The docs state that the interest-rate model is deliberately not publicly disclosed. With the submission switch off, no exposed keeper execution path, and no reproduced attacker-controlled state transition, there is no current code-level bounty finding here. Do not infer a vulnerability from missing disclosure or from an operator-authorized parameter change alone.

## Source-level control flow

`set()` performs the following:
1. Checks facilitator permission (`buds`) and circuit breaker (`bad`).
2. Checks cooldown (`block.timestamp >= tau + toc`) and updates `toc`.
3. Applies bounded `line` and `cap` values.
4. Validates `strBps` against configured range and step; accrues stUSDS yield, then updates `str`.
5. Validates `dutyBps` against configured range and step; accrues Jug duty, then updates `duty`.

No utilization variable is read in this function. This is not by itself a vulnerability: the design may intentionally trust a governance-authorized facilitator and its off-chain decision logic.

## Reopen conditions

1. Re-check `STUSDS_KEEPER_ENABLED` at a new pinned block. Reopen the automated-path hypothesis only if it changes to `1`.
2. If the switch turns on, monitor for the first `Set` event and confirm whether the transaction was submitted by the keeper EOA, the Operator Multisig, or another authorized caller.
3. Seek a reproducible public-input manipulation that changes the keeper's calculated output and a deterministic fork test demonstrating material impact. If the only route requires compromising the authorized EOA, changes to governance configuration, or a privileged operator's improper action, stop this bounty line unless the current program rules explicitly permit it.

## Disposition

Do not submit. The current live automation path is contradicted by the on-chain `STUSDS_KEEPER_ENABLED=0` state. The authorization itself is established, but no public attacker-to-call path or material impact has been demonstrated. Keep only a narrow reactivation monitor; otherwise redirect effort to another in-scope hypothesis.
