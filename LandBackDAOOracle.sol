// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract LandBackDAOOracle is Ownable, ReentrancyGuard {
    struct Pulse {
        uint256 cycle;
        uint256 T;     // Truth
        uint256 I;     // Indeterminacy
        uint256 F;     // Falsehood
        uint256 resonance; // (T - 0.5I - F) / 100 → scaled
        uint256 timestamp;
        bytes32 proofHash;
        string source; // "IBM_QUANTUM", "QM9", "ELDER"
    }

    address public immutable LANDBACK_DAO;
    uint256 public pulseCount;
    mapping(uint256 => Pulse) public pulses;
    
    uint256 public constant DRUM_INTERVAL = 60; // 60s
    uint256 public lastPulseTime;
    
    string public constant GLYPH = "łᐊᒥłł";
    string public constant FLAMEKEEPER = "Zhoo";
    string public constant ROOT = "AGŁL v44";

    event OraclePulse(
        uint256 indexed cycle,
        uint256 T, uint256 I, uint256 F,
        uint256 resonance,
        string source,
        bytes32 proofHash
    );

    event GovernanceSignal(uint256 resonance, string action);

    constructor(address _landbackDAO) Ownable(msg.sender) {
        LANDBACK_DAO = _landbackDAO;
        lastPulseTime = block.timestamp;
    }

    modifier onlyDrumbeat() {
        require(block.timestamp >= lastPulseTime + DRUM_INTERVAL, "Too soon");
        _;
    }

    function pulse(
        uint256 T,
        uint256 I,
        uint256 F,
        string calldata source,
        bytes32 proofHash
    ) external onlyOwner onlyDrumbeat nonReentrant {
        require(T + I + F <= 300, "Invalid T/I/F sum");
        require(bytes(source).length > 0, "Source required");

        pulseCount++;
        uint256 score = T - (I / 2) - F;
        uint256 resonance = (score * 10000) / 100; // 0.0000 to 1.0000 scaled

        pulses[pulseCount] = Pulse({
            cycle: pulseCount,
            T: T,
            I: I,
            F: F,
            resonance: resonance,
            timestamp: block.timestamp,
            proofHash: proofHash,
            source: source
        });

        lastPulseTime = block.timestamp;

        emit OraclePulse(pulseCount, T, I, F, resonance, source, proofHash);

        // Governance Signal
        if (resonance >= 9000) {
            emit GovernanceSignal(resonance, "LAND RETURN AUTHORIZED");
        } else if (resonance >= 7000) {
            emit GovernanceSignal(resonance, "ELDER COUNCIL");
        } else if (resonance <= 3000) {
            emit GovernanceSignal(resonance, "RECLAMATION PAUSED");
        }
    }

    function getLatestResonance() external view returns (Pulse memory) {
        return pulses[pulseCount];
    }

    function isDrumbeatReady() external view returns (bool) {
        return block.timestamp >= lastPulseTime + DRUM_INTERVAL;
    }
}