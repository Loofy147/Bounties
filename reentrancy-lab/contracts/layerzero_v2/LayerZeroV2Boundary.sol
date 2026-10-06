// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title LayerZeroV2BoundaryBenchmark
 * @notice A deliberately small benchmark for the application-side security
 *         boundary exposed by LayerZero V2's OAppReceiver.
 *
 * This is NOT a LayerZero implementation. It models only the semantics that
 * an OApp must enforce once EndpointV2 invokes lzReceive:
 *   1) msg.sender must be the configured local Endpoint;
 *   2) Origin.srcEid must map to the configured peer;
 *   3) the application may then consume the message.
 *
 * Endpoint-side packet verification / payload clearing is modeled separately
 * by MockEndpointV2 below. Keeping the layers separate is intentional:
 * the real EndpointV2 verifies/records the packet and clears the payload
 * before calling the OApp.
 */

struct Origin {
    uint32 srcEid;
    bytes32 sender;
    uint64 nonce;
}

interface ILayerZeroV2Receiver {
    function lzReceive(
        Origin calldata origin,
        bytes32 guid,
        bytes calldata message,
        address executor,
        bytes calldata extraData
    ) external payable;
}

contract BoundaryReceiver is ILayerZeroV2Receiver {
    error OnlyEndpoint(address caller);
    error OnlyPeer(uint32 srcEid, bytes32 sender);
    error BadMessage();

    address public immutable endpoint;
    mapping(uint32 => bytes32) public peers;

    uint256 public receiveCount;
    bytes32 public lastGuid;
    uint256 public lastAmount;

    constructor(address _endpoint) {
        endpoint = _endpoint;
    }

    function setPeer(uint32 srcEid, bytes32 peer) external {
        peers[srcEid] = peer;
    }

    function lzReceive(
        Origin calldata origin,
        bytes32 guid,
        bytes calldata message,
        address,
        bytes calldata
    ) public payable virtual override {
        if (msg.sender != endpoint) revert OnlyEndpoint(msg.sender);
        if (peers[origin.srcEid] != origin.sender) {
            revert OnlyPeer(origin.srcEid, origin.sender);
        }
        _lzReceive(origin, guid, message);
    }

    function _lzReceive(
        Origin calldata,
        bytes32 guid,
        bytes calldata message
    ) internal virtual {
        if (message.length != 32) revert BadMessage();
        uint256 amount;
        assembly {
            amount := calldataload(message.offset)
        }
        receiveCount += 1;
        lastGuid = guid;
        lastAmount = amount;
    }
}

/// MUTATION A: removes the local Endpoint authentication.
/// A correct boundary test must kill this mutant.
contract Mutant_NoEndpointGate is BoundaryReceiver {
    constructor(address _endpoint) BoundaryReceiver(_endpoint) {}

    function lzReceive(
        Origin calldata origin,
        bytes32 guid,
        bytes calldata message,
        address executor,
        bytes calldata extraData
    ) public payable override {
        // MUTATION: endpoint check deleted.
        if (peers[origin.srcEid] != origin.sender) {
            revert OnlyPeer(origin.srcEid, origin.sender);
        }
        _lzReceive(origin, guid, message);
    }
}

/// MUTATION B: removes source-peer authentication.
/// A correct boundary test must kill this mutant.
contract Mutant_NoPeerGate is BoundaryReceiver {
    constructor(address _endpoint) BoundaryReceiver(_endpoint) {}

    function lzReceive(
        Origin calldata origin,
        bytes32 guid,
        bytes calldata message,
        address,
        bytes calldata
    ) public payable override {
        // MUTATION: peer check deleted.
        if (msg.sender != endpoint) revert OnlyEndpoint(msg.sender);
        _lzReceive(origin, guid, message);
    }
}

/**
 * @notice Minimal packet-channel model for the EndpointV2 replay boundary.
 * It intentionally does NOT model DVN signatures or receive libraries.
 * Its sole purpose is to demonstrate the separation:
 *
 * verification/replay state belongs to the channel;
 * Endpoint/peer/origin checks belong to the OApp receiver.
 */
contract MockEndpointV2 {
    mapping(address => mapping(uint32 => mapping(bytes32 => mapping(uint64 => bool)))) public delivered;

    function deliver(
        ILayerZeroV2Receiver receiver,
        Origin calldata origin,
        bytes32 guid,
        bytes calldata message,
        address executor,
        bytes calldata extraData
    ) external {
        if (delivered[address(receiver)][origin.srcEid][origin.sender][origin.nonce]) {
            revert("already-delivered");
        }
        delivered[address(receiver)][origin.srcEid][origin.sender][origin.nonce] = true;
        receiver.lzReceive(origin, guid, message, executor, extraData);
    }
}

/// MUTATION C: removes the channel replay guard.
/// A correct packet-channel test must kill this mutant.
contract Mutant_NoReplayGuard is MockEndpointV2 {
    function deliverUnchecked(
        ILayerZeroV2Receiver receiver,
        Origin calldata origin,
        bytes32 guid,
        bytes calldata message,
        address executor,
        bytes calldata extraData
    ) external {
        receiver.lzReceive(origin, guid, message, executor, extraData);
    }
}
