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
| Production implementation | `OAdapterUpgradeable` @ `0x1ab288...1dd3414`, Sourcify exact-match | ESTABLISHED |
| Proxy type | EIP-1967 TransparentUpgradeableProxy, Sourcify exact-match | ESTABLISHED |
| Endpoint address | `0x1a44076050125825900e736c501f859c50fE728c` | ESTABLISHED |
| Peer mapping | `30423 -> 0xe6a11eb6a514b5510d731e5ed9d8e9294bcaad3b4696fa5d45406d11560b5902` at block 25,989,160; exact official IOTA OFT package | ESTABLISHED |
| DVN configuration | Target-specific app override: 3 required, 1500 confirmations, no optional DVNs; two provider identities established, third remains UNKNOWN | ESTABLISHED_STATE / PARTIAL_IDENTITY |
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
On the source send path, `minAmountLD` must be enforced against the actual `amountReceivedLD`; it is not a destination receive-path parameter.

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

The first blocker is not a security hypothesis. It is **local-fork reproduction plus exact provenance/audit correspondence** beyond the now-pinned direct state:

```
scope address
→ proxy
→ implementation
→ implementation bytecode/source
→ implementation commit/version
→ LayerZero deployment/version
→ applicable audits
```

Current proxy/Endpoint observations are ESTABLISHED, and the implementation bytecode/source identity is ESTABLISHED. The remaining UNKNOWN links are repository commit/version provenance and exact audit correspondence.

See `targets/usdt0/USDT0-FRONTIER-v0.1.md` for the current frontier and evidence ledger.


## Current exact-code evidence

See `targets/usdt0/USDT0-IOTA-LOCKBOX-CODE-MODEL-v0.1.md` and `targets/usdt0/evidence/2026-10-06-iota-lockbox-code-identity.json`.

The deployed implementation is a thin `OAdapterUpgradeable` wrapper over LayerZero's `OFTAdapterUpgradeable`; the current source match is exact, so custom USDT0-specific receive/debit logic is not the primary unexplored surface.
