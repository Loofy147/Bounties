// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @notice Wrapped-asset token. Mint is restricted to its owning Bridge.
contract WrappedToken {
    string public name;
    address public bridge;
    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;

    constructor(string memory _name) {
        name = _name;
        bridge = msg.sender;
    }

    function mint(address to, uint256 amount) external {
        require(msg.sender == bridge, "not bridge");
        balanceOf[to] += amount;
        totalSupply += amount;
    }
}

/// @notice A lock-and-mint bridge endpoint. A trusted off-chain relayer
/// watches deposits on the source chain and signs attestations; this
/// contract verifies the signature and mints.
///
/// THE BUG (real-world shape: KelpDAO/LayerZero, Apr 2026 — $292M; and
/// CrossCurve, Feb 2026 — "missing validation in bridge contract", $3M):
/// the signed message is (depositId, recipient, amount) ONLY. It does
/// NOT bind the destination chain id or this specific bridge contract's
/// address. Any deployment that trusts the same relayer key — which is
/// exactly how shared cross-chain messaging infra like LayerZero gets
/// configured at scale — will accept and mint against the EXACT SAME
/// signed attestation. One real deposit, signed once, mints on every
/// chain sharing that verifier.
contract Bridge {
    address public trustedRelayer;
    WrappedToken public token;
    mapping(bytes32 => bool) public processedLocally; // only guards THIS contract

    constructor(address _trustedRelayer, string memory tokenName) {
        trustedRelayer = _trustedRelayer;
        token = new WrappedToken(tokenName);
    }

    function claim(uint256 depositId, address recipient, uint256 amount, bytes calldata sig) external {
        // BUG: no chainid, no address(this) in the signed payload.
        bytes32 messageHash = keccak256(abi.encodePacked(depositId, recipient, amount));
        bytes32 ethSignedHash = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", messageHash)
        );
        require(!processedLocally[ethSignedHash], "already processed on this chain");
        address signer = recoverSigner(ethSignedHash, sig);
        require(signer == trustedRelayer, "bad signature");

        processedLocally[ethSignedHash] = true; // stops replay WITHIN this contract...
        token.mint(recipient, amount); // ...but does nothing for a sibling deployment
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
}
