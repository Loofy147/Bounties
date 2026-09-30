// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @notice A backend signs vouchers off-chain ("pay X wei to Y"); this
/// contract just checks the signature came from the trusted signer.
/// THE BUG: no nonce, no per-voucher "used" tracking. A signature valid
/// once is valid forever — replay it as many times as the balance allows.
contract SignatureWithdraw {
    address public trustedSigner;

    constructor(address _trustedSigner) {
        trustedSigner = _trustedSigner;
    }

    function fund() external payable {}

    function withdraw(uint256 amount, bytes calldata signature) external {
        bytes32 messageHash = keccak256(abi.encodePacked(msg.sender, amount));
        bytes32 ethSignedHash = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", messageHash)
        );
        address signer = recoverSigner(ethSignedHash, signature);
        require(signer == trustedSigner, "bad signature");

        // BUG: nothing here marks this (msg.sender, amount) voucher as spent.
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "transfer failed");
    }

    function recoverSigner(bytes32 hash, bytes calldata sig) public pure returns (address) {
        require(sig.length == 65, "bad sig length");
        bytes32 r;
        bytes32 s;
        uint8 v;
        assembly {
            r := calldataload(sig.offset)
            s := calldataload(add(sig.offset, 32))
            v := byte(0, calldataload(add(sig.offset, 64)))
        }
        return ecrecover(hash, v, r, s);
    }

    function balance() external view returns (uint256) {
        return address(this).balance;
    }
}
