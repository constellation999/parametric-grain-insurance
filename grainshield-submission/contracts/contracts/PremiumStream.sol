// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./PolicyRegistry.sol";
import "./TriggerOracle.sol";

interface IERC20 {
    function transferFrom(address, address, uint256) external returns (bool);
    function transfer(address, uint256) external returns (bool);
    function balanceOf(address) external view returns (uint256);
}

/// @title PremiumStream — income-linked premium skimming with premium-waiver-by-code
/// @notice Deck §3: "on registered income events, transfers rate x amount from member
///         wallet/aggregator ledger; crisis waiver auto-suspends collection while
///         Stage 1 or 2 is active."
/// @dev Fee-floor note (deck §3 platform table): a ~$0.03 daily skim is only collectable
///      because Hedera's fixed sub-cent USD fees keep tx cost below the payment itself.
contract PremiumStream {
    IERC20 public immutable stable;
    PolicyRegistry public immutable registry;
    TriggerOracle public immutable oracle;
    address public immutable premiumPool; // PayoutRouter holds the pool

    uint16 public constant SKIM_BPS = 50; // 0.5% of income events (deck §1)

    event PremiumSkimmed(address indexed member, uint256 incomeAmount, uint256 premium);
    event PremiumWaived(address indexed member, uint16 regionId, uint256 incomeAmount);

    constructor(address _stable, address _registry, address _oracle, address _premiumPool) {
        stable = IERC20(_stable);
        registry = PolicyRegistry(_registry);
        oracle = TriggerOracle(_oracle);
        premiumPool = _premiumPool;
    }

    /// @notice Called by the member's aggregator when an income event lands on the ledger.
    ///         Member (or aggregator custodial wallet) must have approved this contract.
    function onIncomeEvent(address member, uint256 incomeAmount) external {
        PolicyRegistry.Member memory m = registry.getMember(member);
        require(m.active, "inactive member");
        require(msg.sender == m.aggregator, "not member's aggregator");

        // premium-waiver-by-code: no collection while the region is in crisis
        if (oracle.isCrisisActive(m.regionId)) {
            emit PremiumWaived(member, m.regionId, incomeAmount);
            return;
        }

        uint256 premium = (incomeAmount * SKIM_BPS) / 10_000;
        if (premium == 0) return;
        require(stable.transferFrom(member, premiumPool, premium), "skim failed");
        emit PremiumSkimmed(member, incomeAmount, premium);
    }
}
