// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @notice Treasury with a real-world-shaped bug: initialize() sets the
/// owner but has NO guard against being called again by anyone. This is
/// the exact shape of the 2017 Parity multisig freeze — initWallet() was
/// public and callable by any address, at any time.
contract Treasury {
    address public owner;

    // BUG: no `initialized` flag, no `onlyOwner`/`onlyDeployer` check.
    // Anyone can call this at any time and become owner.
    function initialize(address _owner) external {
        owner = _owner;
    }

    function deposit() external payable {}

    function withdrawAll() external {
        require(msg.sender == owner, "not owner");
        (bool ok, ) = owner.call{value: address(this).balance}("");
        require(ok, "withdraw failed");
    }

    function balance() external view returns (uint256) {
        return address(this).balance;
    }
}
