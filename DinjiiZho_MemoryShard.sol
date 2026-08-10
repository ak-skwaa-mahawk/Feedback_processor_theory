// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract DinjiiZho_MemoryShard is ERC721, Ownable {
    struct Story {
        string elderNameHash;     // SHA3 of name (never on-chain)
        string audioHash;         // IPFS CID of .wav
        string beadworkSVG;       // SVG of family pattern
        string familyLine;        // DNA + ANCSA hash
        uint256 timestamp;
        string glyph;             // łᐊᒥłł variant
    }

    mapping(uint256 => Story) public memories;
    uint256 public storyCount;
    mapping(address => bool) public ritualAuthorized;

    event MemoryForged(uint256 indexed shardId, string familyLine, string glyph);
    event StoryWhispered(uint256 shardId, string audioHash);

    constructor() ERC721("Dinjii Zho' Memory Shard", "DZHO-MEM") Ownable(msg.sender) {}

    modifier onlyRitual() {
        require(ritualAuthorized[msg.sender], "Not ritual authorized");
        _;
    }

    function authorizeRitual(address elder) external onlyOwner {
        ritualAuthorized[elder] = true;
    }

    function mintWithStory(
        address to,
        string memory elderNameHash,
        string memory audioHash,
        string memory beadworkSVG,
        string memory familyLine,
        string memory glyph
    ) external onlyRitual {
        storyCount++;
        _mint(to, storyCount);
        memories[storyCount] = Story(
            elderNameHash, audioHash, beadworkSVG, familyLine, block.timestamp, glyph
        );
        emit MemoryForged(storyCount, familyLine, glyph);
        emit StoryWhispered(storyCount, audioHash);
    }

    // NON-TRANSFERABLE — FAMILY ONLY
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override {
        require(from == address(0) || _isFamilyLine(tokenId, to), "Not family line");
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
    }

    function _isFamilyLine(uint256 tokenId, address to) internal view returns (bool) {
        bytes32 toHash = keccak256(abi.encodePacked(to));
        bytes32 familyHash = keccak256(abi.encodePacked(memories[tokenId].familyLine));
        return toHash == familyHash;
    }
}