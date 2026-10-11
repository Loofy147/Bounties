# USDT0 Audit / Known-Issue Matrix v0.1

Captured: 2026-10-06
Target: Ethereum IOTA Lockbox
Address: `0xAEf027F94008430BF4Fc27FFABB49ea6F1dd3414`
Current implementation evidence: `0x1ab288f49e18884b3a5358f4079ca0f40b891d99` (Sourcify exact_match, Solidity 0.8.22)

## Purpose

This matrix is a **novelty and applicability gate**, not a claim that audited code is safe.

The rule is:

`audit scope + exact code/version correspondence`

must both be established before an old finding can be treated as applicable to the current target.

## Matrix

| Source | Reviewed code/change | Relevant coverage | Target correspondence | State |
|---|---|---|---|---|
| Paladin — Everdawn Final Report, Jan 2025 | `usdt0-oft-contracts` preliminary commit `e6cffe572e9c92e9778c465c04cfae3526a06109`, resolution `a53ae5822b71a091ab07decccbf4f3801965d31b` | Explicitly assessed `OAdapterUpgradeable` on Ethereum and `OUpgradeable` on Ink | Paladin lists canonical Ethereum proxy `0x6C96...` with implementation `0xCD979...`, not the current IOTA lockbox implementation `0x1ab2...` | KNOWN_HISTORICAL, exact-current coverage OPEN |
| Paladin finding 01 | Implementation initializers callable by anyone | `OUpgradeable` / `OAdapterUpgradeable` implementation constructors | Historical resolution marked RESOLVED; current IOTA implementation exact-match source explicitly calls `_disableInitializers()` | KILLED AS CURRENT HYPOTHESIS unless deployment/source correspondence changes |
| OpenZeppelin — Transaction Helper Audit, Nov 2025 | `usdt0-oft-contracts` commit `2ddcf81`, but in-scope files were helper/mixins | System context only for core USDT0 flow | Does not establish review of the current IOTA lockbox implementation | CONTEXT ONLY |
| OpenZeppelin — ERC-7802 Upgrade Audit, Nov 2025 | `usdt0-oft-contracts` PR #63; `OUpgradeable.sol` + `IERC7802.sol` | Differential audit of upgrade changes | Does not directly establish coverage of the Ethereum IOTA `OAdapterUpgradeable` implementation | CONTEXT ONLY |
| Guardian — USDT0 reviews | Multiple `usdt0-oft-contracts` scopes, including later 2026 operational/configuration reviews | Chain/configuration/security context | Exact current IOTA lockbox implementation correspondence not yet established | OPEN |
| Public issue #4 in Everdawn audit repository | User-submitted alleged critical USDT0 bounty claim | Claims unauthorized minting + double redemption | Submission is incomplete and contains multiple `NEEDS YOUR DATA` placeholders; not an accepted finding or primary audit evidence | PUBLIC CLAIM / NOT VALIDATED |
| Public issues #5/#6 | Configuration-resolution investigations | Demonstrates observability/inheritance difficulty | Does not prove a DVN failure; directly motivates the new effective-config resolver | RESEARCH CONTEXT |

## Directly relevant historical observations

### Initialization

Paladin's Issue #01 states that some implementation contracts could be initialized by anyone and records the resolution as **RESOLVED**. The report also notes that for transparent proxies this did not pose a proxy-level risk, although disabling implementation initializers was recommended. citeturn918522view0turn918522view1

Therefore:

`M7 / uninitialized implementation`

is a **regression check**, not an unseeded hypothesis.

### Privileged OApp configuration

Paladin identifies `setPeer`, `setDelegate`, `setMsgInspector`, `setEnforcedOptions`, and `setPreCrime` as owner-controlled functions for `OAdapterUpgradeable`. citeturn918522view1

Therefore a candidate that requires an authorized owner/delegate to behave maliciously must pass the current USDT0 privileged-address scope gate before it can become reportable.

### Code-family correspondence

The audited canonical Ethereum adapter in Paladin's report was:

- proxy: `0x6C96dE32CEa08842dcc4058c14d3aaAD7Fa41dee`
- implementation: `0xCD979B10A55FCdAC23ec785CE3066c6ef8a479A4`

The current IOTA lockbox is:

- proxy: `0xAEf027F94008430BF4Fc27FFABB49ea6F1dd3414`
- implementation: `0x1ab288f49e18884b3a5358f4079ca0f40b891d99`

The existence of the same contract family is not enough to establish exact audit coverage.

## Known-issue kill gate

Before promoting a hypothesis:

1. Compare the target implementation bytecode/source against every applicable audited commit.
2. Check whether the alleged behavior was explicitly discussed.
3. Check whether it was resolved.
4. Check whether the current target is a different deployment/version.
5. If correspondence is incomplete, status stays UNKNOWN rather than upgrading novelty.

## Current decision

No current vulnerability is established.

Audit coverage for the exact IOTA Lockbox implementation remains **UNKNOWN**.

The next discriminating artifact is an exact:

`implementation bytecode/source -> repository commit -> applicable audit scope`

mapping.

## Sources

- Paladin Everdawn Final Report, Jan 2025.
- OpenZeppelin USDT0 Transaction Helper Audit, Nov 2025.
- OpenZeppelin Everdawn USDT0 ERC-7802 Upgrade Audit, Nov 2025.
- Guardian USDT0 public review archive.
- Everdawn-Labs/usdt0-audit-reports public issues.


## Current implementation code identity

Sourcify v2 reports the current implementation address as `exact_match`, with Solidity `0.8.22+commit.4fc1097e` and contract name `OAdapterUpgradeable`. The deployed USDT0-specific contract contains no custom override of the receive, debit, credit, peer, or conversion paths; those are inherited from LayerZero's `OFTAdapterUpgradeable` / `OFTCoreUpgradeable` stack.

This is strong code identity evidence but not repository-commit provenance. Exact audit-version correspondence therefore remains UNKNOWN.
