// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title PolicyRegistry — enrollment via aggregator accounts, two member classes
/// @notice Deck §3 architecture: "enrollment via aggregator accounts; two member classes
///         (buyer-side / seller-side cover); sum insured & class parameters per member."
contract PolicyRegistry {
    enum MemberClass { None, Buyer, Seller }

    struct Member {
        MemberClass cls;
        address aggregator;     // MFI / mobile-money agent who fronts the member
        uint16  regionId;       // pricing region (MWI=1, KEN=2, ETH=3, SOM=4 in the sim)
        uint64  monthlySpend;   // S_k, 6-decimal USD (sim default: $54 -> 54_000000)
        uint64  sumInsuredCap;  // annual payout cap (sim: 0.6 * annual spend = $390)
        uint64  paidOutThisYear;
        bool    active;
    }

    address public owner;
    mapping(address => bool) public isAggregator;
    mapping(address => Member) public members;
    uint256 public memberCount;

    event AggregatorSet(address indexed agg, bool allowed);
    event MemberEnrolled(address indexed member, address indexed aggregator, MemberClass cls, uint16 regionId, uint64 monthlySpend, uint64 sumInsuredCap);
    event MemberDeactivated(address indexed member);

    modifier onlyOwner() { require(msg.sender == owner, "not owner"); _; }
    modifier onlyAggregator() { require(isAggregator[msg.sender], "not aggregator"); _; }

    constructor() { owner = msg.sender; }

    function setAggregator(address agg, bool allowed) external onlyOwner {
        isAggregator[agg] = allowed;
        emit AggregatorSet(agg, allowed);
    }

    /// @notice Aggregators enroll members on their behalf (village-agent mode in the UI mock).
    function enroll(
        address member,
        MemberClass cls,
        uint16 regionId,
        uint64 monthlySpend,
        uint64 sumInsuredCap
    ) external onlyAggregator {
        require(cls != MemberClass.None, "class");
        require(members[member].cls == MemberClass.None, "already enrolled");
        members[member] = Member({
            cls: cls,
            aggregator: msg.sender,
            regionId: regionId,
            monthlySpend: monthlySpend,
            sumInsuredCap: sumInsuredCap,
            paidOutThisYear: 0,
            active: true
        });
        memberCount++;
        emit MemberEnrolled(member, msg.sender, cls, regionId, monthlySpend, sumInsuredCap);
    }

    function deactivate(address member) external {
        require(msg.sender == members[member].aggregator || msg.sender == owner, "auth");
        members[member].active = false;
        emit MemberDeactivated(member);
    }

    /// @dev Called by PayoutRouter to track the annual cap. Router address is set once.
    address public payoutRouter;
    function setPayoutRouter(address r) external onlyOwner {
        require(payoutRouter == address(0), "router set");
        payoutRouter = r;
    }
    function recordPayout(address member, uint64 amount) external {
        require(msg.sender == payoutRouter, "not router");
        members[member].paidOutThisYear += amount;
    }
    function resetAnnual(address member) external onlyOwner {
        members[member].paidOutThisYear = 0; // PoC: manual season reset; production: epoch-based
    }

    function getMember(address m) external view returns (Member memory) { return members[m]; }
}
