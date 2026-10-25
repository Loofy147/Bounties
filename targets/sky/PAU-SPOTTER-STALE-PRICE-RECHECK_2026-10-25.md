# PAU × Spotter stale-price hypothesis — source and deployment recheck (2026-10-25)

**Disposition:** `HYPOTHESIS CONTRADICTED` for the proposed *stale external-asset price lets PAU mint through an allocator vault* mechanism.  
**Scope status:** No vulnerability established. No exploit or production transaction was attempted. This was source, deployment, and governance-document review only.  
**Target:** Sky / `ALLOCATOR-GROVE-A`, Grove Diamond PAU integration.  
**Review date:** 2026-10-25.

## Executive conclusion

The original hypothesis mixes three different accounting layers:

1. **Diamond PAU** allocates funds across integrations through an ALMProxy, controller, and facets. Its USDS facet has a role gate and a per-operation rate limit.
2. **DSS AllocatorVault** draws USDS against a dedicated allocator `ilk` in the Vat. The `ilk` uses a fixed 1:1 allocator oracle and a governance-controlled debt ceiling. It is not a live price feed for the allocator's external holdings.
3. **Vat / Spotter** enforce the current stored per-`ilk` collateral spot and debt ceiling. `Vat.frob` checks the current per-`ilk` debt (`Art × rate ≤ line`) and global debt (`debt ≤ Line`) when debt increases; it also checks the urn's safety using `ink × spot`.

Therefore, the proposed chain — volatile PAU holdings → stale Spotter price → overvalued collateral → allocator minting through that stale price — is not established by the deployed allocator design. The allocator collateral is a large pre-seeded bookkeeping amount and the allocator PIP is a fixed 1:1 oracle. A larger DC-IAM maximum is not evidence of a stale-price bypass or a Vat check bypass.

## Source-to-deployment chain

### 1. PAU entry point

Source: [`USDSFacet.sol`](https://github.com/sky-ecosystem/diamond-pau/blob/dev/src/facets/usds/USDSFacet.sol), repository commit `c5c961a8bd5568c7ca73ba1151b23ab9c7cd9113` as observed in this review.

`USDSFacet.mint(usdsAmount)`:
- requires `ALLOCATOR_ROLE`;
- calls `_decreaseRateLimit(mintRateLimitKey(), usdsAmount)`;
- invokes `AllocatorVault.draw(usdsAmount)` through the ALMProxy;
- transfers the expected USDS amount from the allocator buffer back to the ALMProxy.

This code does not pull an external integration's market price for determining the allocator vault's Vat collateral value.

### 2. Exact Grove vault source and live deployment

- Deployed vault: [Etherscan verified source](https://etherscan.io/address/0xf739a30c74927dc6cFA3B67E4933872a1FC5F4EB#code)
- Source repository: [`sky-ecosystem/dss-allocator`](https://github.com/sky-ecosystem/dss-allocator)
- Pinned dependency commit used by `diamond-pau`: `226584d3b179d98025497815adb4ea585ea0102d`
- Verified contract: `AllocatorVault`, Solidity `0.8.16`
- Constructor parameters decoded from the successful creation transaction:
  - `ilk`: `ALLOCATOR-GROVE-A`
  - `buffer`: `0x436DABce608f73BeA2b75fba35bffe72739697d5`
  - `usdsJoin`: `0x3c0f895007ca717aa01c8693e59df1e8c3777feb`

The deployed source's `draw(wad)` is:
```solidity
uint256 rate = jug.drip(ilk);
uint256 dart = _divup(wad * RAY, rate);
vat.frob(ilk, address(this), address(0), address(this), 0, int256(dart));
usdsJoin.exit(buffer, wad);
```

`Jug.drip` updates the accumulated stability-fee rate; it is not a Spotter price refresh. Debt is then added through `Vat.frob` before USDS exits to the buffer.

### 3. Allocator oracle and deployment initialization

- [Pinned `AllocatorOracle.sol`](https://github.com/sky-ecosystem/dss-allocator/blob/226584d3b179d98025497815adb4ea585ea0102d/src/AllocatorOracle.sol)
- [Pinned `AllocatorInit.sol`](https://github.com/sky-ecosystem/dss-allocator/blob/226584d3b179d98025497815adb4ea585ea0102d/deploy/AllocatorInit.sol)
- [Official Grove onboarding proposal, June 18, 2026](https://vote.sky.money/executive/template-executive-vote-onboard-allocator-grove-a-vault-update-litepsm-parameters-replace-stusds-mom-monthly-settlement-cycle-for-may-2026-staking-rewards-normalization-update-safe-harbor-agreement-prime-agent-proxy-spell-june-18-2026)

`AllocatorOracle.peek()` and `read()` return the constant `WAD = 10**18`; `peek()` reports `ok = true`. There is no live external-asset price, timestamp, or freshness clock in this oracle.

The official onboarding proposal says `AllocatorInit.initIlk` takes the shared `PIP_ALLOCATOR` from Chainlog for this instance, and removes the earlier per-vault `PIP_ALLOCATOR_GROVE_A` Chainlog entry. The pinned initialization code sets `spotter.file(ilk, "pip", sharedInstance.oracle)`, sets `mat = RAY`, calls `spotter.poke(ilk)`, and seeds the vault with `10**12 * WAD` nominal collateral units via `vat.slip` / `vat.grab`. At the fixed 1:1 allocator oracle, that is a deliberately enormous nominal credit-support amount, not the mark-to-market value of PAU investments.

### 4. What the large governance changes do

The official [October 8, 2026 spell](https://vote.sky.money/executive/template-executive-vote-stusds-keeper-launch-monthly-settlement-cycle-for-september-2026-treasury-management-function-parameter-updates-adjust-allocator-grove-a-dc-iam-parameters-update-safe-harbor-agreement-prime-agent-proxy-spells-october-8-2026) raises Grove's DC-IAM **maximum** `line` from 500M to 1.5B USDS, increases target available debt (`gap`) from 25M to 150M, and lengthens the ceiling-increase cooldown from 12 to 24 hours. The September 10 spell had changed the maximum from 25M to 100M and the gap from 5M to 15M.

These are DC-IAM parameter changes governing the maximum, target available debt, and increase cooldown. The maximum is not automatically the currently installed Vat line.

### Pinned read-only mainnet state

A direct, read-only `eth_call` snapshot was taken at Ethereum block **26,267,615** (`0x190cfdf`), not against a local model:

- Chainlog `PIP_ALLOCATOR`: `0xc7b91c401c02b73cbdf424dfaaa60950d5040db7`.
- Chainlog `MCD_SPOT`: `0x65c79fcb50ca1594b025960e539ed7a9a6d434a3`; `MCD_VAT`: `0x35d1b3f3d7966a1dfe207aa4514c12a259a0492b`; `MCD_IAM_AUTO_LINE`: `0xc7bdd1f2b16447dcf3de045c4a039a60ec2f0ba3`.
- `MCD_SPOT.ilks("ALLOCATOR-GROVE-A")` returned `pip = 0xc7b91c401c02b73cbdf424dfaaa60950d5040db7` and `mat = 1e27`. The active Spotter mapping therefore points to the same fixed-price oracle recorded by Chainlog.
- Verified Etherscan source at [that PIP address](https://etherscan.io/address/0xc7b91c401c02b73cbdf424dfaaa60950d5040db7#code) identifies it as `AllocatorOracle`; `peek()` and `read()` both return `1e18` (1:1), and `peek()` is always valid.
- `Vat.ilks("ALLOCATOR-GROVE-A")` returned `rate = 1e27`, `spot = 1e27`, `Art = 120003799741575000000000010` (about **120,003,799.741575 USDS** current debt), and `line = 270003799741575000000000010000000000000000000000000000` rad (about **270,003,799.741575 USDS**).
- `DssAutoLine.ilks("ALLOCATOR-GROVE-A")` returned `line = 1.5B USDS` maximum, `gap = 150M USDS`, `ttl = 86,400 seconds`; its `lastInc` was `2026-10-12 14:01:47 UTC`.

This deployed-state snapshot is consistent with the AutoLine rule that the current Vat line stays near debt plus the configured `gap`, subject to its update/cooldown logic: the observed Vat line is about current debt + 150M USDS, not the 1.5B maximum. This is direct evidence against the claim that the October maximum-parameter change itself instantly set the real Vat line to 1.5B.

At every debt increase, `Vat.frob` still checks the current per-ilk `Art × rate ≤ line`, global `debt ≤ Line`, and the stored `ilk.spot` collateral safety condition. The measured state shows no stale external-asset price flowing into this allocator `ilk`.

## Bounty-eligibility constraints

The current [Sky Immunefi rules](https://immunefi.com/bug-bounty/sky/information/) require a PoC and a vulnerability in deployed code. They explicitly treat oracle-value changes outside governance's parameter assumptions as out of scope; they also treat wards/privileged roles and SubDAO proxies as trusted. The allocator mint path additionally uses role checks and PAU rate limits.

This does not rule out every conceivable PAU or allocator defect. It does mean this specific stale-market-price story currently lacks the required mechanism and also risks conflicting with the program's explicit design and trust assumptions. Do not submit or relabel it as a Critical finding on the current evidence.

## Evidence ledger

| Claim | Label | Evidence / limitation |
|---|---|---|
| Grove vault on mainnet is verified as `AllocatorVault` | `ESTABLISHED` | Etherscan verified source and successful creation transaction; constructor data identifies `ALLOCATOR-GROVE-A`. |
| PAU mint path is role-gated and rate-limited | `ESTABLISHED` | Current public `USDSFacet.sol`. |
| `AllocatorOracle` is constant 1:1 in the pinned source | `ESTABLISHED` | `peek()` and `read()` return `WAD`; no external price input or freshness field. |
| Official onboarding assigns shared `PIP_ALLOCATOR` to Grove's allocator `ilk` | `ESTABLISHED` | Executed onboarding proposal and pinned `AllocatorInit` source. |
| The Sept/Oct ceiling changes create a stale-Spotter window that enables unbacked minting | `CONTRADICTED` | No causal mechanism is shown; these are DC-IAM max/gap/cooldown changes, and `Vat.frob` still enforces debt ceilings and safety. |
| On-chain Chainlog / Spotter / Vat / AutoLine state at block 26,267,615 | `ESTABLISHED` | Direct read-only `eth_call` shows Spotter uses the same constant `PIP_ALLOCATOR`; Vat `spot = 1e27`, actual line ≈ debt + 150M USDS, while AutoLine maximum is 1.5B. This is a pinned block snapshot, not a guarantee against later governance changes. |

## Stop decision and next discriminating check

**Stop** the stale external-asset price hypothesis. The mainnet snapshot now confirms the active `MCD_SPOT` mapping, the fixed oracle implementation, Vat `spot`, actual Vat line, and AutoLine maximum/gap at a single pinned block. No PoC for this stale-price mechanism is justified by the evidence.

Reopen this candidate only if a later official spell or a new pinned state snapshot shows that the active allocator PIP was changed away from the constant oracle, or if a separate, public-call path independently violates the Vat debt/safety invariants. Such a candidate must be evaluated against current scope, known issues, audit disclosures, and role restrictions before local-fork testing. Do not conduct exploit tests against mainnet/public testnet; Sky's program requires authorized local-fork testing.
