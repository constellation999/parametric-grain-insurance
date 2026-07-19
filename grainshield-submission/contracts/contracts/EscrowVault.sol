// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./TriggerOracle.sol";

interface IERC20e {
    function transferFrom(address, address, uint256) external returns (bool);
    function transfer(address, uint256) external returns (bool);
    function balanceOf(address) external view returns (uint256);
}

/// @title EscrowVault — donor tranches with trigger-bound release paths
/// @notice Deck §3: "release paths are trigger-bound — no admin function can divert funds
///         to any address outside the payout router." This is the blockchain commitment
///         layer whose removal raises 25y ruin probability from 0.0% to 18.7% in the sim.
/// @dev The payout router address is immutable and set at construction. There is
///      deliberately NO owner-withdraw function: the credible-commitment property is
///      that donors (and the operator) cannot claw back once deposited. Release requires
///      the oracle to be in Stage1/Stage2 for the region being paid.
contract EscrowVault {
    enum Tranche { Seed, PremiumMatch, ContingentCredit }

    IERC20e public immutable stable;
    TriggerOracle public immutable oracle;
    address public immutable payoutRouter;

    mapping(Tranche => uint256) public trancheBalance;
    uint256 public contingentDrawn; // tracked for the "facility drawn 3.9% of runs" metric

    event Deposited(address indexed donor, Tranche indexed tranche, uint256 amount);
    event Released(Tranche indexed tranche, uint16 indexed regionId, uint256 amount);

    constructor(address _stable, address _oracle, address _payoutRouter) {
        stable = IERC20e(_stable);
        oracle = TriggerOracle(_oracle);
        payoutRouter = _payoutRouter;
    }

    function deposit(Tranche tranche, uint256 amount) external {
        require(stable.transferFrom(msg.sender, address(this), amount), "transfer");
        trancheBalance[tranche] += amount;
        emit Deposited(msg.sender, tranche, amount);
    }

    /// @notice Only the router can pull, only during an active trigger, only to itself.
    function release(Tranche tranche, uint16 regionId, uint256 amount) external {
        require(msg.sender == payoutRouter, "not router");
        require(oracle.isCrisisActive(regionId), "no active trigger");
        require(trancheBalance[tranche] >= amount, "tranche insufficient");
        trancheBalance[tranche] -= amount;
        if (tranche == Tranche.ContingentCredit) contingentDrawn += amount;
        require(stable.transfer(payoutRouter, amount), "transfer");
        emit Released(tranche, regionId, amount);
    }

    function totalEscrowed() external view returns (uint256) {
        return stable.balanceOf(address(this));
    }
}
