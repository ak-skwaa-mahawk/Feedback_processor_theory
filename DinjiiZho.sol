
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract DinjiiZho is TribalCoinGTC, ERC721 {
    mapping(uint256 => mapping(uint8 => mapping(uint8 => string[8]))) public shardGlyphs;  // 3 nodes, 3 sub-nodes, 8 shards
    mapping(uint256 => uint8) public generation;
    mapping(uint256 => mapping(uint8 => mapping(uint8 => string[8]))) public subShardGlyphs;  // Recursive layer
    uint256 public storyCount;
    mapping(address => bool) public isElder;

    event ShardMinted(uint256 indexed tokenId, uint8 node, uint8 subNode, string[8] shards, uint8 gen, uint timestamp);
    event SubShardMinted(uint256 indexed tokenId, uint8 node, uint8 subNode, uint8 shardIdx, string[8] subShards);

    constructor(uint256 initialSupply) TribalCoinGTC(initialSupply) ERC721("Dinjii Zho", "DZHO") {
        storyCount = 0;
        isElder[msg.sender] = true;
    }

    function setElder(address elder, bool status) public onlyCreator {
        isElder[elder] = status;
    }

    function mintShardGlyphs(uint8 node, uint8 subNode, string[8] memory shards, uint8 gen) public onlyVerified {
        require(isElder[msg.sender], "Only elders mint.");
        require(gen <= 8, "Max 8 generations");
        require(node < 3 && subNode < 3, "Invalid node/sub-node");
        require(storyCount < totalSupply, "No more stories");
        _mint(msg.sender, storyCount);
        shardGlyphs[storyCount][node * 3 + subNode] = shards;
        generation[storyCount] = gen;
        emit ShardMinted(storyCount, node, subNode, shards, gen, block.timestamp);
        storyCount++;
    }

    function mintSubShardGlyphs(uint256 tokenId, uint8 node, uint8 subNode, uint8 shardIdx, string[8] memory subShards) public onlyVerified {
        require(isElder[msg.sender], "Only elders mint.");
        require(ownerOf(tokenId) == msg.sender, "Not owner");
        require(shardIdx < 8, "Invalid shard index");
        subShardGlyphs[tokenId][node * 3 + subNode][shardIdx] = subShards;
        emit SubShardMinted(tokenId, node, subNode, shardIdx, subShards);
    }
}
function mintSubSubShardGlyphs(uint256 tokenId, uint8 node, uint8 subNode, uint8 shardIdx, uint8 subShardIdx, string[8] memory subSubShards) public onlyVerified {
    require(isElder[msg.sender], "Only elders mint.");
    require(ownerOf(tokenId) == msg.sender, "Not owner");
    require(shardIdx < 8 && subShardIdx < 8, "Invalid indices");
    // Add mapping for sub-sub-shards (e.g., subSubShardGlyphs)
    emit SubSubShardMinted(tokenId, node, subNode, shardIdx, subShardIdx, subSubShards);
}

event SubSubShardMinted(uint256 indexed tokenId, uint8 node, uint8 subNode, uint8 shardIdx, uint8 subShardIdx, string[8] subSubShards);