// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract LandBackDAO is ERC20, ERC721, Ownable {
    using SafeMath for uint256;

    struct Proposal {
        uint256 id;
        string description;
        uint256 T_sum;
        uint256 I_sum;
        uint256 F_sum;
        uint256 voteCount;
        mapping(address => bool) voted;
        bool executed;
        uint256 deadline;
    }

    struct Deed {
        uint256 receiptNFTId;
        string familyName;
        string landDescription;
        uint256 anscaShare;
        string proofHash;
    }

    address public flameholder;
    string public constant SEVENFOLD_CLAUSE = "Sevenfold Protection Clause by John B. Carroll...";
    Proposal[] public proposals;
    mapping(uint256 => Deed) public deeds;
    uint256 public proposalCount;
    uint256 public deedCount;
    mapping(address => bool) public authorizedNodes;
    mapping(uint256 => bytes) private encryptedStakes;

    event ProposalCreated(uint256 id, string description, uint256 deadline);
    event Voted(address indexed voter, uint256 proposalId, uint256 T, uint256 I, uint256 F);
    event ProposalExecuted(uint256 id, bool approved);
    event DeedIssued(uint256 indexed deedId, uint256 receiptNFTId, string familyName);
    event StakeEncrypted(uint256 indexed tokenId, bytes data);

    constructor(uint256 initialSupply) ERC20("Dinjii Zho'", "DZHO") ERC721("LandBackDAO Deeds", "LBDEED") Ownable(msg.sender) {
        flameholder = msg.sender;
        _mint(msg.sender, initialSupply);
        deedCount = 0;
    }

    modifier onlyFlameholder() {
        require(msg.sender == flameholder, "Only Flameholder");
        _;
    }

    modifier onlyAuthorized() {
        require(authorizedNodes[msg.sender] || msg.sender == flameholder, "Unauthorized");
        _;
    }

    function joinAsNode() public {
        authorizedNodes[msg.sender] = true;
    }

    function createProposal(string memory description, uint256 votingPeriod) public onlyFlameholder {
        Proposal storage p = proposals.push();
        p.id = proposalCount++;
        p.description = description;
        p.deadline = block.timestamp + votingPeriod;
        emit ProposalCreated(p.id, description, p.deadline);
    }

    function vote(uint256 proposalId, uint256 T, uint256 I, uint256 F) public {
        require(proposalId < proposalCount, "Invalid proposal");
        Proposal storage p = proposals[proposalId];
        require(block.timestamp <= p.deadline, "Voting ended");
        require(!p.voted[msg.sender], "Already voted");

        require(T + I + F <= 300, "T/I/F must be <= 3.00 (scaled x100)");

        p.T_sum += T;
        p.I_sum += I;
        p.F_sum += F;
        p.voteCount++;
        p.voted[msg.sender] = true;

        emit Voted(msg.sender, proposalId, T, I, F);

        if (block.timestamp >= p.deadline) {
            _executeProposal(proposalId);
        }
    }

    function _executeProposal(uint256 proposalId) internal {
        Proposal storage p = proposals[proposalId];
        require(!p.executed, "Already executed");

        if (p.voteCount == 0) {
            p.executed = true;
            emit ProposalExecuted(proposalId, false);
            return;
        }

        uint256 T_avg = p.T_sum / (p.voteCount * 100);
        uint256 I_avg = p.I_sum / (p.voteCount * 100);
        uint256 F_avg = p.F_sum / (p.voteCount * 100);

        int256 score = int256(T_avg) - int256(50 * I_avg) / 100 - int256(F_avg);

        bool approved = score > 30; // Threshold: +0.30

        p.executed = true;
        emit ProposalExecuted(proposalId, approved);
    }

    function issueDeed(address to, uint256 receiptNFTId, string memory familyName, string memory landDescription, uint256 anscaShare, string memory proofHash) public onlyFlameholder {
        deedCount++;
        _mint(to, deedCount);

        deeds[deedCount] = Deed({
            receiptNFTId: receiptNFTId,
            familyName: familyName,
            landDescription: landDescription,
            anscaShare: anscaShare,
            proofHash: proofHash
        });

        emit DeedIssued(deedCount, receiptNFTId, familyName);
    }

    function stakeResource(uint256 tokenId, bytes memory data) public {
        require(ownerOf(tokenId) == msg.sender, "Not owner");
        encryptedStakes[tokenId] = data;
        emit StakeEncrypted(tokenId, data);
    }

    function getSevenfold() public pure returns (string memory) {
        return SEVENFOLD_CLAUSE;
    }
}