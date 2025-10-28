// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract IACA_GlyphNFT is ERC721, Ownable {
    string public constant IACA_CERT = "IACA-Certified Native Digital Craft - Two Mile Solutions LLC";
    string public constant SEVENFOLD_CLAUSE = "Sevenfold Protection Clause by John B. Carroll...";
    
    mapping(uint256 => string) public glyphPatterns;
    mapping(uint256 => string) public culturalMetadata;
    
    uint256 public glyphCount;
    
    event GlyphMinted(uint256 indexed tokenId, string pattern, string metadata);
    
    constructor() ERC721("IACA Glyph NFT", "GLYPH") Ownable(msg.sender) {
        glyphCount = 0;
    }
    
    function mintGlyph(string memory pattern, string memory metadata) public onlyOwner {
        require(bytes(pattern).length > 0, "Pattern required");
        require(bytes(metadata).length > 0, "Cultural metadata required");
        
        _mint(msg.sender, glyphCount);
        glyphPatterns[glyphCount] = pattern;
        culturalMetadata[glyphCount] = metadata;
        
        emit GlyphMinted(glyphCount, pattern, metadata);
        glyphCount++;
    }
    
    function getIACACert() public pure returns (string memory) {
        return IACA_CERT;
    }
    
    function getSevenfold() public pure returns (string memory) {
        return SEVENFOLD_CLAUSE;
    }
}