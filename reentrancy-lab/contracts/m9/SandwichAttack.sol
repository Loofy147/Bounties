// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract VulnToken {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    uint256 public totalSupply;

    constructor(uint256 initialSupply) {
        totalSupply = initialSupply;
        balanceOf[msg.sender] = initialSupply;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        _transfer(msg.sender, to, amount);
        return true;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        allowance[from][msg.sender] -= amount;
        _transfer(from, to, amount);
        return true;
    }

    function _transfer(address from, address to, uint256 amount) internal {
        require(balanceOf[from] >= amount, "balance");
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
    }
}

/// @notice Same constant-product AMM shape as M3. THE BUG here is
/// different, though: it's not the oracle being trusted elsewhere --
/// it's that swapETHForToken() takes NO minimum-output parameter. Any
/// caller has zero protection against the price moving between when
/// they signed their transaction and when it actually lands on-chain.
contract SimpleAMM {
    VulnToken public token;
    uint256 public reserveETH;
    uint256 public reserveToken;

    constructor(VulnToken _token) {
        token = _token;
    }

    /// Caller must have already sent `tokenAmount` of TOKEN directly to
    /// this contract's address before calling, since VulnToken here has
    /// no privileged pull-based mint step for the pool itself.
    function seedLiquidity(uint256 tokenAmount) external payable {
        require(reserveETH == 0 && reserveToken == 0, "already seeded");
        require(token.balanceOf(address(this)) >= tokenAmount, "fund the pool with tokens first");
        reserveETH = msg.value;
        reserveToken = tokenAmount;
    }

    function priceTokenInETH() public view returns (uint256) {
        if (reserveToken == 0) return 0;
        return (reserveETH * 1e18) / reserveToken;
    }

    /// THE BUG: no minTokenOut parameter. Whatever the pool's price is
    /// the instant this executes, the caller accepts it -- no matter
    /// how it got there.
    function swapETHForToken() external payable returns (uint256 tokenOut) {
        uint256 k = reserveETH * reserveToken;
        uint256 newReserveETH = reserveETH + msg.value;
        uint256 newReserveToken = k / newReserveETH;
        tokenOut = reserveToken - newReserveToken;
        reserveETH = newReserveETH;
        reserveToken = newReserveToken;
        token.transfer(msg.sender, tokenOut);
    }

    /// The fix, included for contrast: caller states the minimum
    /// they'll accept; the trade reverts instead of silently executing
    /// at a manipulated price.
    function swapETHForTokenProtected(uint256 minTokenOut) external payable returns (uint256 tokenOut) {
        uint256 k = reserveETH * reserveToken;
        uint256 newReserveETH = reserveETH + msg.value;
        uint256 newReserveToken = k / newReserveETH;
        tokenOut = reserveToken - newReserveToken;
        require(tokenOut >= minTokenOut, "slippage: price moved past your limit");
        reserveETH = newReserveETH;
        reserveToken = newReserveToken;
        token.transfer(msg.sender, tokenOut);
    }

    function swapTokenForETH(uint256 tokenIn) external returns (uint256 ethOut) {
        token.transferFrom(msg.sender, address(this), tokenIn);
        uint256 k = reserveETH * reserveToken;
        uint256 newReserveToken = reserveToken + tokenIn;
        uint256 newReserveETH = k / newReserveToken;
        ethOut = reserveETH - newReserveETH;
        reserveETH = newReserveETH;
        reserveToken = newReserveToken;
        (bool ok, ) = msg.sender.call{value: ethOut}("");
        require(ok, "eth send failed");
    }

    receive() external payable {}
}
