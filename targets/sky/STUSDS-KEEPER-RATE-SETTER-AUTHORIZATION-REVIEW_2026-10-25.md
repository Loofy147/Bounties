# stUSDS Keeper / Rate Setter — Authorization Boundary Review

Date: 2026-10-25
Status: OPEN — code-level boundary confirmed; exploitability and live-state checks remain unproven.
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
- UNKNOWN — whether the currently deployed Chainlog address and on-chain `buds`, `tau`, `toc`, `bad`, `strCfg`, and `dutyCfg` match the spell's intended post-state at the latest block.
- UNKNOWN — the keeper's implementation, its actual trigger/decision algorithm, data inputs, sampling windows, and whether it has any separate on-chain role beyond `buds`.
- HYPOTHESIS — a keeper can submit a bounded but economically inappropriate rate change at a utilization boundary, producing material loss or withdrawal impairment.
- NOT ESTABLISHED — no attacker-controlled route, profitable state transition, insolvency, theft, or bounty-eligible impact has been demonstrated.

## Source-level control flow

`set()` performs the following:
1. Checks facilitator permission (`buds`) and circuit breaker (`bad`).
2. Checks cooldown (`block.timestamp >= tau + toc`) and updates `toc`.
3. Applies bounded `line` and `cap` values.
4. Validates `strBps` against configured range and step; accrues stUSDS yield, then updates `str`.
5. Validates `dutyBps` against configured range and step; accrues Jug duty, then updates `duty`.

No utilization variable is read in this function. This is not by itself a vulnerability: the design may intentionally trust a governance-authorized facilitator and its off-chain decision logic.

## Next discriminating tests

1. Resolve the current mainnet `STUSDS_RATE_SETTER` from Chainlog at a pinned block; verify bytecode/source match.
2. Read `buds(keeper)`, `wards`, `bad`, `tau`, `toc`, `maxLine`, `maxCap`, `strCfg`, and `dutyCfg` at that same block.
3. Identify the keeper's deployed implementation and exact function that calls `set()`; trace its utilization data source, freshness, averaging window, threshold logic, and transaction submission behavior.
4. Build a local fork test that reproduces the boundary state, then test whether a public actor can manipulate the keeper's input or timing to cause a material rate error despite step/cooldown bounds.
5. Quantify a concrete impact against documented bounty categories. If only an authorized keeper makes an allowed but poor decision, classify as operational/trust assumption and kill the bounty lead absent a code-enforced invariant violation.

## Disposition

Keep as a focused investigation, not a submitted finding. The missing proof is the attacker-to-impact path through the keeper's actual deployed logic, not merely the absence of an on-chain utilization check.
