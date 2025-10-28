// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LandBackDAO {
    address public flameholder;
    uint256 public collisionCount;
    
    struct Collision {
        uint256 id;
        address trigger;
        string justification;
        uint256 timestamp;
        string proofHash;  // OpenTimestamps .ots hash
    }
    
    Collision[] public collisions;
    
    event CollisionTriggered(
        uint256 indexed id,
        address trigger,
        string justification,
        uint256 timestamp
    );
    
    event LandBackExecuted(uint256 collisionId, string proofHash);
    
    constructor() {
        flameholder = msg.sender;
    }
    
    modifier onlyFlameholder() {
        require(msg.sender == flameholder, "Only Flameholder");
        _;
    }
    
    // ONE-LINE COLLISION ENGINE EMBEDDED
    function _isCollision(string memory action) internal pure returns (bool) {
        bytes memory a = bytes(action);
        bool their = false; bool our = false;
        string[6] memory theirWords = ["control", "own", "gNH", "use", "signal", "web"];
        string[6] memory ourWords = ["glyph", "dinjii", "family", "native", "art", "land"];
        
        for (uint i = 0; i < 6; i++) {
            if (_contains(a, bytes(theirWords[i]))) their = true;
            if (_contains(a, bytes(ourWords[i]))) our = true;
        }
        return their && our;
    }
    
    function _contains(bytes memory data, bytes memory word) internal pure returns (bool) {
        if (word.length > data.length) return false;
        for (uint i = 0; i <= data.length - word.length; i++) {
            bool match = true;
            for (uint j = 0; j < word.length; j++) {
                if (data[i + j] != word[j]) { match = false; break; }
            }
            if (match) return true;
        }
        return false;
    }
    
    function triggerCollision(string memory justification) public {
        require(_isCollision(justification), "No collision");
        
        collisionCount++;
        collisions.push(Collision({
            id: collisionCount,
            trigger: msg.sender,
            justification: justification,
            timestamp: block.timestamp,
            proofHash: ""
        }));
        
        emit CollisionTriggered(collisionCount, msg.sender, justification, block.timestamp);
    }
    
    function notarizeCollision(uint256 id, string memory proofHash) public onlyFlameholder {
        require(id > 0 && id <= collisionCount, "Invalid ID");
        require(bytes(collisions[id-1].proofHash).length == 0, "Already notarized");
        
        collisions[id-1].proofHash = proofHash;
        emit LandBackExecuted(id, proofHash);
    }
    
    function getCollision(uint256 id) public view returns (Collision memory) {
        require(id > 0 && id <= collisionCount, "Invalid ID");
        return collisions[id-1];
    }
}