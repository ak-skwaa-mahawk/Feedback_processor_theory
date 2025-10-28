// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract NeutrosophicDAO {
    address public flameholder;
    string public constant SEVENFOLD_CLAUSE = "Sevenfold Protection Clause by John B. Carroll...";
    
    struct Agent {
        address addr;
        string name;
        bool active;
    }
    
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
    
    Agent[] public agents;
    Proposal[] public proposals;
    uint256 public proposalCount;
    
    event AgentJoined(address indexed agent, string name);
    event ProposalCreated(uint256 id, string description, uint256 deadline);
    event Voted(address indexed voter, uint256 proposalId, uint256 T, uint256 I, uint256 F);
    event ProposalExecuted(uint256 id, bool approved);
    
    modifier onlyFlameholder() {
        require(msg.sender == flameholder, "Only Flameholder");
        _;
    }
    
    modifier onlyAgent() {
        bool isAgent = false;
        for (uint i = 0; i < agents.length; i++) {
            if (agents[i].addr == msg.sender && agents[i].active) {
                isAgent = true;
                break;
            }
        }
        require(isAgent, "Not authorized agent");
        _;
    }
    
    constructor() {
        flameholder = msg.sender;
    }
    
    function joinAsAgent(string memory name) public {
        require(msg.sender != flameholder, "Flameholder is supreme");
        agents.push(Agent(msg.sender, name, true));
        emit AgentJoined(msg.sender, name);
    }
    
    function createProposal(string memory description, uint256 votingPeriod) public onlyFlameholder {
        Proposal storage p = proposals.push();
        p.id = proposalCount++;
        p.description = description;
        p.deadline = block.timestamp + votingPeriod;
        emit ProposalCreated(p.id, description, p.deadline);
    }
    
    function vote(uint256 proposalId, uint256 T, uint256 I, uint256 F) public onlyAgent {
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
        
        // Auto-execute if voting complete
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
        
        // Normalize to [0,1]
        uint256 T_avg = p.T_sum / (p.voteCount * 100);
        uint256 I_avg = p.I_sum / (p.voteCount * 100);
        uint256 F_avg = p.F_sum / (p.voteCount * 100);
        
        // Neutrosophic Decision: T - 0.5*I - F
        int256 score = int256(T_avg) - int256(50 * I_avg) / 100 - int256(F_avg);
        
        bool approved = score > 30; // Threshold: +0.30
        
        p.executed = true;
        emit ProposalExecuted(proposalId, approved);
    }
    
    function getProposal(uint256 id) public view returns (
        string memory description,
        uint256 T_sum, uint256 I_sum, uint256 F_sum,
        uint256 voteCount, bool executed, uint256 deadline
    ) {
        Proposal storage p = proposals[id];
        return (p.description, p.T_sum, p.I_sum, p.F_sum, p.voteCount, p.executed, p.deadline);
    }
    
    function getSevenfold() public pure returns (string memory) {
        return SEVENFOLD_CLAUSE;
    }
}