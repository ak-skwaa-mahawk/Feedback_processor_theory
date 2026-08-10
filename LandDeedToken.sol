// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract LandDeedToken is ERC721, Ownable {
    uint256 public deedCount;
    
    struct Deed {
        uint256 receiptNFTId;  // Links to Handshake Return NFT
        string familyName;
        string landDescription;
        uint256 anscaShare;
        string proofHash;
    }
    
    mapping(uint256 => Deed) public deeds;
    
    event DeedIssued(
        uint256 indexed deedId,
        uint256 receiptNFTId,
        string familyName,
        string landDescription
    );
    
    constructor() ERC721("Land Deed Token", "DEED") Ownable(msg.sender) {}
    
    function issueDeed(
        address to,
        uint256 receiptNFTId,
        string memory familyName,
        string memory landDescription,
        uint256 anscaShare,
        string memory proofHash
    ) public onlyOwner {
        deedCount++;
        _mint(to, deedCount);
        
        deeds[deedCount] = Deed({
            receiptNFTId: receiptNFTId,
            familyName: familyName,
            landDescription: landDescription,
            anscaShare: anscaShare,
            proofHash: proofHash
        });
        
        emit DeedIssued(deedCount, receiptNFTId, familyName, landDescription);
    }
    
    function getDeed(uint256 deedId) public view returns (Deed memory) {
        return deeds[deedId];
    }
}