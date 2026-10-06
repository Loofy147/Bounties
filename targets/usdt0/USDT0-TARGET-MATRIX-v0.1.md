# USDT0 Target Matrix v0.1

Captured: 2026-10-06
Program scope revision: 2026-09-30

## Selected P0 target

| Field | Value | Status |
|---|---|---|
| Program | USDT0 / Immunefi | ESTABLISHED |
| Target | OApp Adapter Ethereum (IOTA) | ESTABLISHED |
| Added | 2026-09-30 | ESTABLISHED |
| Ethereum address | `0xAEf027F94008430BF4Fc27FFABB49ea6F1dd3414` | ESTABLISHED |
| Ethereum Chain ID | 1 | ESTABLISHED |
| Ethereum LayerZero EID | 30101 | ESTABLISHED |
| IOTA LayerZero EID | 30423 | ESTABLISHED |
| Route | Ethereum ↔ IOTA only | ESTABLISHED |
| Platform-reported funds | $111.6K | ESTABLISHED as platform snapshot |
| EVM critical max | $6M | ESTABLISHED |
| Critical minimum | $50K | ESTABLISHED |
| PoC | Required | ESTABLISHED |
| Mainnet/public-testnet testing | Prohibited | ESTABLISHED |
| Production implementation | — | UNKNOWN |
| Proxy type | EIP-1967 | ESTABLISHED |
| Endpoint address | `0x1a44076050125825900e736c501f859c50fE728c` | ESTABLISHED |
| Peer mapping | — | UNKNOWN |
| DVN configuration | — | UNKNOWN |
| Audit coverage for this exact deployment | — | UNKNOWN |
| Prior disclosure/known issue | — | UNKNOWN |
| Vulnerability | None claimed | ESTABLISHED |

## Security model

```
Ethereum USDT
   ↓
IOTA Lockbox / OApp Adapter
   ↓
LayerZero Endpoint
   ↓
verified message
   ↓
IOTA OApp / OFT
   ↓
USDT0 on IOTA L1
```

Return path:

```
IOTA USDT0 burn
   ↓
LayerZero message
   ↓
Ethereum lockbox authorization
   ↓
USDT release
```

The current USDT0 documentation states that IOTA USDT0 is not directly connected to the other USDT0 chains; Ethereum is the bridge point for that route.

## First research invariants

### LZ-BOUNDARY-01
Only the configured local Endpoint can enter the receiver boundary.

### LZ-BOUNDARY-02
For the IOTA source/destination path, the LayerZero origin EID and configured peer must agree with the intended counterpart.

### LZ-ACCOUNT-01
Every authorized unlock on Ethereum corresponds to an authorized burn/transfer state on IOTA under the documented route semantics.

### LZ-ACCOUNT-02
Every authorized mint on IOTA corresponds to the corresponding Ethereum lock state under the documented route semantics.

### LZ-AMOUNT-01
Shared/local-decimal conversion does not create or destroy material value outside the documented dust/conversion rules.

### LZ-AMOUNT-02
A user-specified `minAmountLD` cannot be bypassed by the receive path.

### LZ-UPGRADE-01
Proxy implementation, initializer state, admin/delegate authority, and storage layout remain mutually consistent.

## Research gates

Do not create a vulnerability claim from any one invariant alone.

```
G0 scope
G1 exact deployed version
G2 invariant violation
G3 isolated reproduction
G4 in-scope impact
G5 permitted/realistic attacker preconditions
G6 audit/known-issue/novelty
G7 minimal PoC
G8 human review
```

## Current blocker

The first blocker is not a security hypothesis. It is **production correspondence** beyond the currently observed proxy/Endpoint layer:

```
scope address
→ proxy
→ implementation
→ implementation bytecode/source
→ implementation commit/version
→ LayerZero deployment/version
→ applicable audits
```

Current proxy/Endpoint observations are recorded as ESTABLISHED from secondary evidence, but target-level code conclusions remain UNKNOWN until the full chain is established.

See `targets/usdt0/USDT0-FRONTIER-v0.1.md` for the current frontier and evidence ledger.
