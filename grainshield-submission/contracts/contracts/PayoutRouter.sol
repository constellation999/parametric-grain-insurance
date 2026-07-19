// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./PolicyRegistry.sol";
import "./TriggerOracle.sol";
import "./EscrowVault.sol";

interface IERC20r {
    function transfer(address, uint256) external returns (bool);
    function balanceOf(address) external view returns (uint256);
}

/// @title PayoutRouter — waterfall settlement in stablecoin to aggregator accounts
/// @notice Deck §3: "waterfall logic (reserves -> hedger caps -> reinsurance recovery ->
///         first loss -> contingent credit); settles in stablecoin to aggregator accounts."
///         Payout formula from the simulation (sim.py):
///           pay_k = S_k * max(0, min(r_k, 2.25) - 1.25), annual cap = sumInsured;
///           plus a fixed early payment on Stage 1.
/// @dev PoC waterfall: own premium reserves -> escrow Seed -> escrow PremiumMatch ->
///      escrow ContingentCredit. Hedger caps and reinsurance recovery are off-chain
///      legs in production and are represented here by the escrow tranches.
contract PayoutRouter {
    IERC20r public immutable stable;
    PolicyRegistry public immutable registry;
    TriggerOracle public immutable oracle;
    EscrowVault public escrow; // set once after escrow deployment (circular dep)

    address public owner;
    uint64 public constant EARLY_PAYMENT = 35_000000; // $35, 6 decimals (sim: satellite stage)
    uint64 public constant ATTACHMENT_1E4 = 12500;
    uint64 public constant CAP_1E4 = 22500;

    mapping(address => bool) public earlyPaid; // per member per episode (reset with oracle)

    event EarlyPayout(address indexed member, address indexed aggregator, uint256 amount);
    event MainPayout(address indexed member, address indexed aggregator, uint256 amount, uint64 ratio1e4);
    event WaterfallDraw(uint8 indexed level, uint256 amount); // 0=reserves 1=seed 2=match 3=contingent

    modifier onlyOwner() { require(msg.sender == owner, "not owner"); _; }

    constructor(address _stable, address _registry, address _oracle) {
        stable = IERC20r(_stable);
        registry = PolicyRegistry(_registry);
        oracle = TriggerOracle(_oracle);
        owner = msg.sender;
    }

    function setEscrow(address _escrow) external onlyOwner {
        require(address(escrow) == address(0), "escrow set");
        escrow = EscrowVault(_escrow);
    }

    /// @notice Anyone can execute a due payout (permissionless keeper pattern) —
    ///         "no claims, no adjusters, no committees."
    function executeEarlyPayout(address member) external {
        PolicyRegistry.Member memory m = registry.getMember(member);
        require(m.active, "inactive");
        require(oracle.stageOf(m.regionId) != TriggerOracle.Stage.None, "no stage1");
        require(!earlyPaid[member], "already paid");
        earlyPaid[member] = true;

        uint256 amount = _capToSumInsured(m, EARLY_PAYMENT);
        _fund(m.regionId, amount);
        registry.recordPayout(member, uint64(amount));
        require(stable.transfer(m.aggregator, amount), "transfer");
        emit EarlyPayout(member, m.aggregator, amount);
    }

    function executeMainPayout(address member) external {
        PolicyRegistry.Member memory m = registry.getMember(member);
        require(m.active, "inactive");
        require(oracle.stageOf(m.regionId) == TriggerOracle.Stage.Stage2Confirmed, "no stage2");

        uint64 r = oracle.ratioOf(m.regionId);
        uint64 rc = r > CAP_1E4 ? CAP_1E4 : r;
        require(rc > ATTACHMENT_1E4, "below attachment");
        // pay = S * (min(r,cap) - attachment), all 1e4-scaled ratios
        uint256 pay = (uint256(m.monthlySpend) * (rc - ATTACHMENT_1E4)) / 10_000;
        pay = _capToSumInsured(m, pay);
        require(pay > 0, "cap reached");

        _fund(m.regionId, pay);
        registry.recordPayout(member, uint64(pay));
        require(stable.transfer(m.aggregator, pay), "transfer");
        emit MainPayout(member, m.aggregator, pay, r);
    }

    /// @dev Waterfall: draw from escrow tranches until this contract's balance covers `needed`.
    function _fund(uint16 regionId, uint256 needed) internal {
        uint256 bal = stable.balanceOf(address(this));
        if (bal >= needed) { emit WaterfallDraw(0, needed); return; }
        uint256 gap = needed - bal;

        EscrowVault.Tranche[3] memory order = [
            EscrowVault.Tranche.Seed,
            EscrowVault.Tranche.PremiumMatch,
            EscrowVault.Tranche.ContingentCredit
        ];
        for (uint8 i = 0; i < 3 && gap > 0; i++) {
            uint256 avail = escrow.trancheBalance(order[i]);
            uint256 draw = avail >= gap ? gap : avail;
            if (draw > 0) {
                escrow.release(order[i], regionId, draw);
                emit WaterfallDraw(i + 1, draw);
                gap -= draw;
            }
        }
        require(gap == 0, "insolvent: all layers exhausted");
    }

    function _capToSumInsured(PolicyRegistry.Member memory m, uint256 pay) internal pure returns (uint256) {
        uint256 remaining = m.sumInsuredCap > m.paidOutThisYear
            ? m.sumInsuredCap - m.paidOutThisYear : 0;
        return pay > remaining ? remaining : pay;
    }

    /// @notice Owner resets per-episode early-payment flags after oracle reset.
    function resetEarlyPaid(address[] calldata membersList) external onlyOwner {
        for (uint i = 0; i < membersList.length; i++) earlyPaid[membersList[i]] = false;
    }
}
