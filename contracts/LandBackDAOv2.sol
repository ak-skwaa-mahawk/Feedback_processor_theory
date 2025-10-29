// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract LandBackDAOv2 is Ownable, ReentrancyGuard {
    struct QuantumBallot {
        uint256 T;     // Truth (0-100)
        uint256 I;     // Indeterminacy (0-100)
        uint256 F;     // Falsehood (0-100)
        uint256 resonance; // (T - 0.5I - F)/100
        address voter;
        uint256 timestamp;
        bytes32 proofHash;
        string source;
    }

    struct Proposal {
        uint256 id;
        string description;
        uint256 voteCount;
        uint256 totalResonance;
        uint256 startTime;
        uint256 endTime;
        bool executed;
        mapping(address => bool) hasVoted;
    }

    address[] public members;
    mapping(address => bool) public isMember;
    
    uint256 public proposalCount;
    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => QuantumBallot[]) public ballots;

    uint256 public constant QUORUM = 8500;
    uint256 public constant VOTING_PERIOD = 7 days;
    uint256 public constant DRUM_HZ = 60;
    
    string public constant GLYPH = "łᐊᒥłł";
    string public constant FLAMEKEEPER = "Zhoo";

    event QuantumVote(uint256 indexed proposalId, address voter, uint256 resonance, string source);
    event ProposalCreated(uint256 indexed id, string description);
    event ProposalExecuted(uint256 indexed id, bool success);

    constructor(address[] memory _members) Ownable(msg.sender) {
        for (uint i = 0; i < _members.length; i++) {
            isMember[_members[i]] = true;
            members.push(_members[i]);
        }
    }

    function createProposal(string calldata description) external onlyOwner {
        proposalCount++;
        Proposal storage p = proposals[proposalCount];
        p.id = proposalCount;
        p.description = description;
        p.startTime = block.timestamp;
        p.endTime = block.timestamp + VOTING_PERIOD;
        emit ProposalCreated(proposalCount, description);
    }

    function castQuantumVote(
        uint256 proposalId,
        uint256 T,
        uint256 I,
        uint256 F,
        string calldata source,
        bytes32 proofHash
    ) external nonReentrant {
        require(isMember[msg.sender], "Not a member");
        Proposal storage p = proposals[proposalId];
        require(block.timestamp >= p.startTime && block.timestamp <= p.endTime, "Voting closed");
        require(!p.hasVoted[msg.sender], "Already voted");
        require(T + I + F <= 300, "Invalid T/I/F");

        uint256 score = T - (I / 2) - F;
        uint256 resonance = (score * 10000) / 100;

        QuantumBallot memory ballot = QuantumBallot({
            T: T, I: I, F: F, resonance: resonance,
            voter: msg.sender, timestamp: block.timestamp,
            proofHash: proofHash, source: source
        });

        ballots[proposalId].push(ballot);
        p.voteCount++;
        p.totalResonance += resonance;
        p.hasVoted[msg.sender] = true;

        emit QuantumVote(proposalId, msg.sender, resonance, source);

        if (p.voteCount >= 3 && averageResonance(proposalId) >= QUORUM) {
            p.executed = true;
            emit ProposalExecuted(proposalId, true);
        }
    }

    function averageResonance(uint256 proposalId) public view returns (uint256) {
        Proposal storage p = proposals[proposalId];
        if (p.voteCount == 0) return 0;
        return p.totalResonance / p.voteCount;
    }
}