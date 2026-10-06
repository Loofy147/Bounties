# LayerZero V2 Boundary Benchmark

Status: **EXPERIMENTALLY_SUPPORTED** after local benchmark implementation; not a statement about any USDT0 target.

## Purpose

This module closes a specific abstraction gap in M6.

M6 demonstrates generic cross-deployment signature/domain replay. LayerZero V2 does not use that exact mechanism at the OApp boundary. The current LayerZero V2 source defines `OAppReceiver.lzReceive()` with two application-side checks:

1. the caller must be the local Endpoint;
2. `Origin.sender` must equal the configured peer for `Origin.srcEid`.

The Endpoint itself separately verifies/records packets and clears the stored payload before invoking the receiver.

The benchmark therefore keeps three layers separate:

`Endpoint channel state -> OApp boundary -> application message semantics`

The benchmark is intentionally small and dependency-free. It is not a substitute for importing or executing the real LayerZero contracts.

## Source-derived model

Current LayerZero V2 references used for the model:

- `OAppReceiver.lzReceive(origin, guid, message, executor, extraData)`
- `OAppCore.peers[srcEid]`
- `EndpointV2.verify(origin, receiver, payloadHash)`
- `EndpointV2.lzReceive(...)` payload clearing before receiver execution
- `OFTCore._lzReceive()` using `origin.srcEid` and OFT message fields
- `OFTMsgCodec` shared/local decimal representation

Primary-source interpretation:

- Endpoint authentication is an application boundary invariant.
- Peer authentication is an application boundary invariant.
- Packet verification/replay is a channel invariant.
- `executor` and `extraData` are execution context and must not be confused with message origin.
- `srcEid`, EVM `chainId`, and peer address are distinct namespaces.

## Benchmark fixtures

### Secure baseline

`BoundaryReceiver`

Enforces:

`caller == endpoint`

and

`peers[srcEid] == origin.sender`

before consuming the message.

### Mutant A

`Mutant_NoEndpointGate`

Removes only the Endpoint caller check.

Expected invariant failure:

`untrusted caller -> receiver state transition`

### Mutant B

`Mutant_NoPeerGate`

Removes only the peer check.

Expected invariant failure:

`trusted endpoint + untrusted origin sender -> receiver state transition`

### Mutant C

`Mutant_NoReplayGuard`

Removes the packet-channel replay guard.

Expected invariant failure:

`same (receiver, srcEid, sender, nonce) -> second economic effect`

## Acceptance criteria

The benchmark is considered valid only if:

- secure baseline accepts the valid packet;
- direct attacker call is rejected;
- trusted endpoint + wrong peer is rejected;
- duplicate packet is rejected by the modeled channel;
- each mutation produces the corresponding forbidden state transition;
- the test is deterministic.

## Important boundary

The benchmark does NOT assert that a missing check inside an actual USDT0/LayerZero deployment is automatically a bounty finding.

For a real target we still need:

`scope -> deployed target -> version -> violated invariant -> reproduction -> in-scope impact -> novelty`

## Next extension

After this benchmark passes:

1. add compose sender/Endpoint boundary fixtures;
2. add OFT amountLD/amountSD conversion and `minAmountLD` invariants;
3. add ordered/unordered nonce semantics;
4. add target adapter for a real USDT0 deployment;
5. add evidence-bundle output.
