// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @notice A deliberately vulnerable ETH vault. Deposits are tracked per-user;
/// withdraw() sends ETH BEFORE zeroing the balance — classic reentrancy bug.
contract VulnerableVault {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "no balance");

        // VULNERABLE: external call happens before state update.
        // A malicious receive()/fallback() can re-enter withdraw()
        // while balances[msg.sender] still shows the old (unzeroed) amount.
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "transfer failed");

        balances[msg.sender] = 0; // <-- too late
    }

    function vaultBalance() external view returns (uint256) {
        return address(this).balance;
    }
}
