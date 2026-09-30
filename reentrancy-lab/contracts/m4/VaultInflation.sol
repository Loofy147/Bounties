// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract Asset {
    string public name = "Asset";
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    uint256 public totalSupply;

    constructor(uint256 supply) {
        totalSupply = supply;
        balanceOf[msg.sender] = supply;
    }

    function transfer(address to, uint256 amt) external returns (bool) {
        _transfer(msg.sender, to, amt);
        return true;
    }

    function approve(address spender, uint256 amt) external returns (bool) {
        allowance[msg.sender][spender] = amt;
        return true;
    }

    function transferFrom(address from, address to, uint256 amt) external returns (bool) {
        allowance[from][msg.sender] -= amt;
        _transfer(from, to, amt);
        return true;
    }

    function _transfer(address from, address to, uint256 amt) internal {
        balanceOf[from] -= amt;
        balanceOf[to] += amt;
    }
}

/// @notice Minimal ERC4626-style share vault. THE BUG: totalAssets() reads
/// the vault's raw token balance instead of internally tracked deposits,
/// so anyone can inflate share price by donating tokens directly via
/// transfer() (bypassing deposit()) — the classic "first depositor" /
/// "donation" / "inflation" attack found in dozens of real audits.
contract SimpleVault {
    Asset public asset;
    uint256 public totalShares;
    mapping(address => uint256) public sharesOf;

    constructor(Asset _asset) {
        asset = _asset;
    }

    function totalAssets() public view returns (uint256) {
        return asset.balanceOf(address(this)); // <-- the bug: raw balance, not internal accounting
    }

    function deposit(uint256 assets) external returns (uint256 shares) {
        if (totalShares == 0) {
            shares = assets; // 1:1 on first deposit
        } else {
            shares = (assets * totalShares) / totalAssets(); // rounds DOWN
            // NOTE: no `require(shares > 0)` guard here — and that's the
            // realistic case. Many real vault implementations omit it,
            // which is exactly why this class of bug still shows up in
            // audits today: the deposit silently "succeeds" for zero shares.
        }
        asset.transferFrom(msg.sender, address(this), assets);
        totalShares += shares;
        sharesOf[msg.sender] += shares;
    }

    function redeem(uint256 shares) external returns (uint256 assets) {
        assets = (shares * totalAssets()) / totalShares;
        sharesOf[msg.sender] -= shares;
        totalShares -= shares;
        asset.transfer(msg.sender, assets);
    }
}
