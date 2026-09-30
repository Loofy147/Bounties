// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @notice The shared logic contract that one or more proxies delegatecall
/// into. THE BUG: nothing ever calls initialize() on THIS contract's own
/// address directly -- everyone assumes users only ever interact through
/// a Proxy. But Implementation is a real, independently deployed contract
/// with its own address and its own storage. Anyone can call it directly.
contract Implementation {
    bool public initialized;
    address public admin;
    uint256 public value;

    function initialize(address _admin) external {
        require(!initialized, "already initialized");
        initialized = true;
        admin = _admin;
    }

    function setValue(uint256 _value) external {
        require(msg.sender == admin, "not admin");
        value = _value;
    }

    /// A realistic "emergency admin" escape hatch -- exactly the shape
    /// that turned the 2017 Parity multisig bug from "one wallet
    /// compromised" into "every wallet sharing this library, frozen".
    function destroy() external {
        require(msg.sender == admin, "not admin");
        selfdestruct(payable(admin));
    }
}

/// @notice Minimal delegatecall proxy. Its OWN storage is completely
/// separate from Implementation's storage -- initialize() called through
/// the proxy sets up the PROXY's admin, in the PROXY's storage slots.
/// That's normal and safe. The bug lives entirely in Implementation
/// being independently callable.
contract Proxy {
    // EIP-1967 unstructured storage slot: keccak256("eip1967.proxy.implementation") - 1.
    // Landed on here the hard way -- an earlier version of this contract stored
    // `implementation` as a normal state variable at slot 0, which collided
    // with Implementation's `bool initialized` (also slot 0). Every initialize()
    // call read the nonzero implementation address as a truthy bool and reverted
    // "already initialized" before ever actually being initialized. That's a
    // second real vulnerability class (proxy/implementation storage collision),
    // discovered by literally writing the naive version of this contract.
    bytes32 private constant IMPLEMENTATION_SLOT =
        0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc;

    constructor(address _implementation) {
        bytes32 slot = IMPLEMENTATION_SLOT;
        assembly {
            sstore(slot, _implementation)
        }
    }

    function implementation() public view returns (address impl) {
        bytes32 slot = IMPLEMENTATION_SLOT;
        assembly {
            impl := sload(slot)
        }
    }

    fallback() external payable {
        address impl = implementation();
        assembly {
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(gas(), impl, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result
            case 0 { revert(0, returndatasize()) }
            default { return(0, returndatasize()) }
        }
    }

    receive() external payable {}
}
