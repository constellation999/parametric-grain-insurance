// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title TriggerOracle — two-stage state machine with multi-source median confirmation
/// @notice Deck §3: "Stage 1: satellite composite (NDVI/CHIRPS/SMAP) crosses threshold ->
///         EarlyPayout event. Stage 2: entitlement ratio (USD import-parity or wage-to-grain,
///         multi-source median) confirms -> MainPayout. Multi-index conjunction: no single
///         feed can fire a payout."
/// @dev PoC simplification: feeds are permissioned reporter addresses posting values;
///      the contract itself computes the median over the latest round — so no single
///      reporter can fire Stage 2. On Hedera production, reports arrive as HCS-ordered
///      attestations and this contract reads the sequenced topic.
contract TriggerOracle {
    enum Stage { None, Stage1Active, Stage2Confirmed }

    struct RegionState {
        Stage   stage;
        uint64  satelliteIndex;   // scaled 1e4: composite z / threshold ratio
        uint64  entitlementRatio; // r_k scaled 1e4: 12500 = 1.25 attachment
        uint64  stage1Since;
        uint64  stage2Since;
    }

    // r thresholds from the simulation (sim.py): attachment 1.25, cap 2.25
    uint64 public constant ATTACHMENT_1E4 = 12500;
    uint64 public constant CAP_1E4        = 22500;
    // satellite composite threshold (stylized detection 0.70 in the sim; roadmap item 1
    // replaces this with a CHIRPS/MODIS backtest)
    uint64 public constant SAT_THRESHOLD_1E4 = 10000;

    address public owner;
    mapping(address => bool) public isReporter;
    uint8 public reporterCount;
    uint8 public constant MIN_REPORTS = 3; // multi-source median needs >= 3 feeds

    mapping(uint16 => RegionState) public regions;
    // regionId => round => reporter => value; regionId => round => values posted
    mapping(uint16 => mapping(uint64 => uint64[])) internal roundValues;
    mapping(uint16 => mapping(uint64 => mapping(address => bool))) internal reported;
    mapping(uint16 => uint64) public currentRound;

    event ReporterSet(address indexed reporter, bool allowed);
    event SatelliteUpdate(uint16 indexed regionId, uint64 value);
    event EarlyPayoutTriggered(uint16 indexed regionId, uint64 satelliteIndex);
    event EntitlementReport(uint16 indexed regionId, uint64 round, address indexed reporter, uint64 value);
    event MainPayoutConfirmed(uint16 indexed regionId, uint64 medianRatio);
    event RegionReset(uint16 indexed regionId);

    modifier onlyOwner() { require(msg.sender == owner, "not owner"); _; }
    modifier onlyReporter() { require(isReporter[msg.sender], "not reporter"); _; }

    constructor() { owner = msg.sender; }

    function setReporter(address reporter, bool allowed) external onlyOwner {
        if (allowed && !isReporter[reporter]) reporterCount++;
        if (!allowed && isReporter[reporter]) reporterCount--;
        isReporter[reporter] = allowed;
        emit ReporterSet(reporter, allowed);
    }

    /// @notice Stage 1 — satellite composite crossing fires the early partial payout signal.
    function postSatellite(uint16 regionId, uint64 value1e4) external onlyReporter {
        RegionState storage r = regions[regionId];
        r.satelliteIndex = value1e4;
        emit SatelliteUpdate(regionId, value1e4);
        if (value1e4 >= SAT_THRESHOLD_1E4 && r.stage == Stage.None) {
            r.stage = Stage.Stage1Active;
            r.stage1Since = uint64(block.timestamp);
            emit EarlyPayoutTriggered(regionId, value1e4);
        }
    }

    /// @notice Stage 2 — reporters post entitlement ratios; median over >= MIN_REPORTS confirms.
    /// @dev Conjunction: Stage 2 can only confirm while Stage 1 is active.
    function postEntitlement(uint16 regionId, uint64 ratio1e4) external onlyReporter {
        RegionState storage r = regions[regionId];
        require(r.stage == Stage.Stage1Active, "stage1 not active");
        uint64 round = currentRound[regionId];
        require(!reported[regionId][round][msg.sender], "already reported");
        reported[regionId][round][msg.sender] = true;
        roundValues[regionId][round].push(ratio1e4);
        emit EntitlementReport(regionId, round, msg.sender, ratio1e4);

        uint64[] storage vals = roundValues[regionId][round];
        if (vals.length >= MIN_REPORTS) {
            uint64 med = _median(vals);
            if (med >= ATTACHMENT_1E4) {
                r.entitlementRatio = med;
                r.stage = Stage.Stage2Confirmed;
                r.stage2Since = uint64(block.timestamp);
                emit MainPayoutConfirmed(regionId, med);
            }
            currentRound[regionId] = round + 1; // open next round either way
        }
    }

    /// @notice Crisis over — owner resets (production: automatic on ratio decay below exit).
    function resetRegion(uint16 regionId) external onlyOwner {
        delete regions[regionId];
        emit RegionReset(regionId);
    }

    // ---- views used by the rest of the system ----
    function isCrisisActive(uint16 regionId) external view returns (bool) {
        Stage s = regions[regionId].stage;
        return s == Stage.Stage1Active || s == Stage.Stage2Confirmed; // premium waiver condition
    }
    function stageOf(uint16 regionId) external view returns (Stage) { return regions[regionId].stage; }
    function ratioOf(uint16 regionId) external view returns (uint64) { return regions[regionId].entitlementRatio; }

    function _median(uint64[] storage a) internal view returns (uint64) {
        uint64[] memory b = new uint64[](a.length);
        for (uint i = 0; i < a.length; i++) b[i] = a[i];
        // insertion sort — arrays are tiny (3-7 reporters)
        for (uint i = 1; i < b.length; i++) {
            uint64 key = b[i]; uint j = i;
            while (j > 0 && b[j-1] > key) { b[j] = b[j-1]; j--; }
            b[j] = key;
        }
        return b[b.length / 2];
    }
}
