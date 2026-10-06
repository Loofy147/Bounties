# LayerZero Effective Configuration Resolver

Status: **OPEN / UNVERIFIED** as a production-data tool; the deterministic resolver regression itself is ready for authoritative CI execution.

## Problem

LayerZero V2 permits OApp-specific configuration overrides and default-library inheritance. Therefore:

`app getConfig == empty`

does **not** imply:

`requiredDVNCount == 0`

An empty application-level configuration can inherit effective settings from the selected/default receive library.

## Resolver contract

Input snapshot:

- local EID
- remote EID
- OApp address
- application-selected receive library, if any
- Endpoint default receive library, if applicable
- application ULN config
- receive-library defaults
- executor config
- optional historical reconstruction

Output:

- RESOLVED or UNRESOLVED
- effective receive library
- required DVNs
- optional DVNs
- optional threshold
- confirmations
- executor
- provenance chain
- warnings

## Precedence

```
explicit OApp config
        ↓
selected receive library
        ↓
receive-library default ULN config
        ↓
historical reconstruction
        ↓
UNRESOLVED
```

Historical reconstruction is kept separate because an RPC snapshot alone cannot prove past state.

## Why this matters to USDT0

The public USDT0 audit-repository investigation #5/#6 reported cases where application-level ULN configuration appeared empty and concluded that effective configuration reconstruction required additional tracing; it explicitly did not treat the result as evidence of a DVN security failure.

The resolver converts that ambiguity into a deterministic research artifact:

`observed config -> resolution path -> effective trust set -> provenance`

This is useful both for:

- killing false hypotheses caused by misreading empty config;
- identifying genuine configuration mismatches once the live and historical evidence are complete.

## Security boundary

The resolver itself does not prove:

- a DVN is honest;
- a configuration is economically safe;
- an OApp is vulnerable;
- a bounty impact exists.

It only establishes the effective configuration state that later hypotheses depend on.

## Next extension

Add a live acquisition layer that records:

- Endpoint `defaultReceiveLibrary(eid)`
- OApp `getConfig`
- ReceiveUln302 default ULN config
- OApp `peers(eid)`
- historical `ReceiveLibrarySet`, `UlnConfigSet`, `DefaultReceiveLibrarySet`, `DefaultUlnConfigsSet` events
- exact block numbers and RPC provenance

Then compare the resolved result with the target's observed `PacketVerified` / `PacketDelivered` traffic.
