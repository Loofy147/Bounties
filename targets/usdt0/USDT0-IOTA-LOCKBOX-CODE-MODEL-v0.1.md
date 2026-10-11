# USDT0 Ethereum IOTA Lockbox — Deployed Code Model v0.1

Captured: 2026-10-06

Target:
- address: `0xAEf027F94008430BF4Fc27FFABB49ea6F1dd3414`
- Ethereum chain ID: 1
- LayerZero EID: 30101
- IOTA EID: 30423
- implementation observed by Dedaub live-RPC reference: `0x1ab288f49e18884b3a5358f4079ca0f40b891d99`

## Code identity

### Implementation

Sourcify API v2 reports:

- match: **exact_match**
- compiler: `0.8.22+commit.4fc1097e`
- contract name: `OAdapterUpgradeable`
- creation bytecode: exact_match
- runtime bytecode: exact_match
- ABI: available
- deployed source includes `contracts/OAdapterUpgradeable.sol`

This establishes deployed bytecode/source correspondence for the implementation address.

It does **not** establish the original Git repository commit used to build it. Repository commit/version correspondence remains UNKNOWN.

### Custom implementation surface

The deployed USDT0-specific contract is:

```solidity
contract OAdapterUpgradeable is OFTAdapterUpgradeable {
    constructor(address _token, address _lzEndpoint)
        OFTAdapterUpgradeable(_token, _lzEndpoint)
    {
        _disableInitializers();
    }

    function initialize(address _delegate) public initializer {
        __OFTAdapter_init(_delegate);
        __Ownable_init(_delegate);
    }
}
```

No custom override of:
- `lzReceive`
- `_lzReceive`
- `_credit`
- `_debit`
- `_debitView`
- `_toLD`
- `_toSD`
- `setPeer`
- `isPeer`

was found in this exact implementation source.

## Receive path

The inherited `OAppReceiverUpgradeable.lzReceive` performs:

1. `msg.sender == endpoint`
2. `peer(origin.srcEid) == origin.sender`
3. dispatch to `_lzReceive`

The inherited `OFTCoreUpgradeable._lzReceive` then:

1. decodes `sendTo` from the OFT message;
2. decodes `amountSD`;
3. converts with `_toLD(amountSD)`;
4. calls `_credit(toAddress, amountLD, origin.srcEid)`;
5. emits `OFTReceived`;
6. optionally queues compose data.

The inherited `OFTAdapterUpgradeable._credit` performs:

```
innerToken.safeTransfer(to, amountLD)
return amountLD
```

Therefore the Ethereum receive-side value release is upstream LayerZero adapter behavior, guarded before entry by Endpoint + peer checks.

## Send / lock path

The inherited `OFTAdapterUpgradeable._debit`:

1. calls `_debitView`;
2. receives `amountSentLD` and `amountReceivedLD`;
3. executes `innerToken.safeTransferFrom(from, address(this), amountSentLD)`.

The inherited `_debitView`:

1. removes local-decimal dust;
2. sets `amountReceivedLD = amountSentLD`;
3. reverts when `amountReceivedLD < minAmountLD`.

Thus `minAmountLD` is a **source-side send constraint**. It is not carried into `lzReceive` and is not rechecked on the destination receive path.

This corrects the earlier target matrix wording.

## Decimal path

The exact source uses LayerZero's standard SD/LD conversion functions:

```
_toLD(amountSD) = amountSD * decimalConversionRate
_toSD(amountLD) = uint64(amountLD / decimalConversionRate)
_removeDust(amountLD) =
    floor(amountLD / decimalConversionRate) * decimalConversionRate
```

USDT0's developer documentation specifies:
- USDT0/IOTA shared decimals = 6
- IOTA local decimals = 6
- IOTA fee = 0 bps

For this route the documented decimal regime therefore has no expected rounding loss.

A target-level statement still requires the deployed token decimals and current configuration to be pinned in the permitted fork.

## Initialization

The exact implementation constructor explicitly calls `_disableInitializers()`.

Therefore the historical audit observation concerning implementation initialization is a **killed current hypothesis** unless a future code/version mismatch is established.

## Configuration surface

The implementation inherits:
- `peers[eid]`
- `setPeer(eid, peer)` owner-only
- `setDelegate(delegate)` owner-only
- Endpoint-selected send/receive libraries
- Endpoint-forwarded library configuration

Configuration correctness therefore remains a deployment/state problem rather than a custom implementation-code problem.

## Current security interpretation

### ESTABLISHED
- exact deployed implementation/source match;
- implementation is a thin `OFTAdapterUpgradeable` subclass;
- implementation constructor disables initializers;
- receive boundary checks Endpoint then peer;
- Ethereum credit releases underlying USDT via `safeTransfer`;
- send path locks USDT via `safeTransferFrom`;
- `minAmountLD` is checked on source-side debit;
- OFT receive amount originates from encoded `amountSD`.

### UNKNOWN
- exact USDT0 repository commit for this implementation;
- proxy-to-implementation linkage by a primary RPC observation in our current evidence bundle;
- actual current peer bytes32 value at EID 30423;
- actual current Endpoint receive library;
- actual current effective receive ULN configuration at a pinned block;
- historical configuration transitions;
- exact historical audit scope correspondence to this implementation.

### NONE_CLAIMED
No vulnerability is established.

## Research consequence

The highest-value target-specific lane is now:

```
deployment state
    >
custom implementation logic
```

Specifically:

```
peer(30423)
+ receive library(30423)
+ ReceiveUln configuration
+ configuration history
+ Endpoint packet verification/delivery
+ IOTA-side source identity
```

Do not spend additional cycles on invented USDT0-specific `_credit` or `_debit` logic unless the implementation correspondence changes.
