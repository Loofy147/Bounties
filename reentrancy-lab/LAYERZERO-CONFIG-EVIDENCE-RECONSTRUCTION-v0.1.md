# LayerZero Configuration Evidence Reconstruction v0.1

Captured: 2026-10-06
Target: USDT0 Ethereum IOTA Lockbox
Target address: `0xAEf027F94008430BF4Fc27FFABB49ea6F1dd3414`
Local EID: 30101
Remote EID: 30423

## Objective

Recover the **effective** LayerZero receive configuration for the IOTA route without treating incomplete RPC reads as proof of an insecure configuration.

The reconstruction must explain both current state and the state transitions that produced it.

## Protocol facts used by this specification

LayerZero V2's `MessageLibManager` resolves an OApp's receive library from an application-specific value and, when unset, the default receive library for the source EID. It also supports a grace-period timeout for a previous receive library.

The receive library `ReceiveUln302` exposes the ULN configuration through `getConfig(eid, oapp, CONFIG_TYPE_ULN)`.

The send-side `SendUln302` separately exposes Executor configuration and send-side ULN configuration.

Therefore the evidence model keeps receive and send domains separate.

## State model

### Receive-library selection

```
app receiveLibrary[oapp][srcEid]
        |
        | zero / default
        v
defaultReceiveLibrary[srcEid]
        |
        +--> defaultReceiveLibraryTimeout[srcEid]
        |
        v
effective receive library
```

### Receive-side ULN config

```
effective receive library
        |
        v
ReceiveUln302.getConfig(srcEid, oapp, CONFIG_TYPE_ULN)
        |
        v
UlnBase field-level merge
        |
        +--> required DVNs
        +--> optional DVNs / threshold
        +--> confirmations
```

`UlnBase` semantics must be preserved during reconstruction:
- DVN count `0` = DEFAULT / inherit;
- DVN count `255` = NONE / literal empty;
- confirmations `0` = DEFAULT / inherit;
- confirmations `uint64.max` = literal zero;
- final effective config must contain at least one DVN.

### Send-side context

```
effective send library
        |
        v
SendUln302.getConfig(dstEid, oapp, CONFIG_TYPE_EXECUTOR)
        |
        +--> executor
        +--> maxMessageSize
```

Send-side executor state must never be reported as the receive-side DVN configuration.

## Required snapshot

```json
{
  "chain_id": 1,
  "local_eid": 30101,
  "remote_eid": 30423,
  "oapp": "0x...",
  "block_number": 0,
  "block_hash": "0x...",
  "target_code_hash": "0x...",
  "receive_library": {
    "app_value": "0x...",
    "default_value": "0x...",
    "effective_value": "0x...",
    "timeout": {
      "library": "0x...",
      "expiry_block": 0
    }
  },
  "receive_uln": {
    "required_dvns": [],
    "optional_dvns": [],
    "optional_threshold": 0,
    "confirmations": 0,
    "source": "rpc|event_reconstruction"
  },
  "send_context": {
    "send_library": "0x...",
    "executor": "0x...",
    "max_message_size": 0
  }
}
```

Values are placeholders until collected from a permitted fork.

## Historical event ledger

For each relevant event:

| Field | Requirement |
|---|---|
| block_number | mandatory |
| block_hash | mandatory |
| transaction_hash | mandatory |
| emitter | mandatory |
| topic0 | mandatory |
| ABI revision | mandatory |
| decoded parameters | mandatory |
| observation timestamp | mandatory |
| source RPC | mandatory |

The event ledger is not itself the state. State is the deterministic fold of valid events plus the deployment initialization state.

## Minimum event families

Receive / peer:
- `PeerSet`
- `ReceiveLibrarySet`
- `DefaultReceiveLibrarySet`
- `ReceiveLibraryTimeoutSet`

Receive-side message-lib configuration:
- `UlnConfigSet` emitted by the applicable receive library
- applicable default configuration events for the deployed LayerZero message-library version

Execution / send context:
- applicable send-library configuration events
- `ExecutorConfigSet` where emitted by the deployed library version

Do not assume an event exists merely because a current source revision contains a similarly named setter. ABI/event names must be verified against the deployed implementation revision.

## Resolution algorithm

1. Pin the fork block.
2. Verify target code identity at that block.
3. Read direct state for current values.
4. Determine application-selected receive library.
5. Resolve default receive library when application value is unset.
6. Apply only a valid grace-period override when the deployed protocol version supports it and the pinned state proves it is active.
7. Query the effective receive library's ULN configuration.
8. Separately query send-side Executor/ULN configuration.
9. Compare current state with event-folded state.
10. If any required input is missing, return **UNRESOLVED**.

## Evidence states

- RESOLVED: all inputs and provenance are present.
- PARTIAL: some values are observed but one or more dependencies remain unresolved.
- UNRESOLVED: the effective state cannot be derived without unsupported assumptions.
- CONFLICTED: direct state and event reconstruction disagree.

The last state is a stop condition requiring investigation, not a reason to select the more convenient value.

## Security use

A resolved configuration may support later hypotheses about:
- incorrect peer;
- unexpected receive library;
- weakened DVN quorum;
- stale-library acceptance;
- configuration transition races.

It does not, by itself, establish exploitability or bounty impact.

## Stop conditions

Stop target escalation when:
- deployment/source correspondence is unknown;
- event history is incomplete at a security-relevant transition;
- only a secondary source proves a critical value and primary verification is possible;
- an alleged attack needs privileged behavior excluded by program scope;
- the observation cannot be reproduced on the permitted fork.

## Source code references

- MessageLibManager: https://github.com/LayerZero-Labs/LayerZero-v2/blob/main/packages/layerzero-v2/evm/protocol/contracts/MessageLibManager.sol
- ReceiveUln302: https://github.com/LayerZero-Labs/LayerZero-v2/blob/main/packages/layerzero-v2/evm/messagelib/contracts/uln/uln302/ReceiveUln302.sol
- SendUln302: https://github.com/LayerZero-Labs/LayerZero-v2/blob/main/packages/layerzero-v2/evm/messagelib/contracts/uln/uln302/SendUln302.sol
- EndpointV2: https://github.com/LayerZero-Labs/LayerZero-v2/blob/main/packages/layerzero-v2/evm/protocol/contracts/EndpointV2.sol
