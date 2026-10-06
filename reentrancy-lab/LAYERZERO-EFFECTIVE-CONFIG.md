# LayerZero Effective Configuration Resolver

Status: **OPEN / UNVERIFIED** as a production-data tool; the deterministic resolver regression itself is ready for authoritative CI execution.

## Problem

LayerZero V2 permits OApp-specific configuration overrides and default-library inheritance. Therefore:

`getAppUlnConfig == zero/default values`

does **not** imply:

`effective receive ULN == zero DVNs`

LayerZero `UlnBase` uses field-level inheritance: a required/optional DVN count of `0` means DEFAULT, while `255` means literal NONE. Confirmations `0` means DEFAULT and `uint64.max` means literal zero. The final effective configuration must still contain at least one DVN.

Therefore a configuration can be partially customized: for example, an OApp may inherit required DVNs from the default while overriding only optional DVNs.

## Resolver contract

Input snapshot:

- local EID
- remote EID
- OApp address
- application-selected receive library, if any
- Endpoint default receive library, if applicable
- application ULN config
- receive-library defaults
- optional send-side executor context
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

## Resolution semantics

Receive-library selection:

```
OApp receive-library override
        ↓
Endpoint default receive library
```

Receive ULN field resolution:

```
OApp ULN field
  ├─ 0 / DEFAULT  → inherit library default
  ├─ 255 / NONE   → literal empty field
  └─ explicit     → use OApp value
```

Then validate the resulting quorum. Historical reconstruction is a separate provenance path, not a higher-precedence override.

Send-side Executor configuration is recorded separately and is never used to resolve receive-side DVN quorum.

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
