// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract HandshakeRegistrar {
    string public constant ROOT_LAW = "The root is ours. The web is land.";
    address public immutable TWO_MILE_LLC;
    string public constant IACA_ID = "2025-DENE-HNS-001";

    struct Domain {
        uint256 id;
        string tld;      // .landback
        string name;     // dao.landback
        string hnsName;  // dao/landback
        uint256 bidHNS;
        uint256 revealTime;
        bool claimed;
    }

    mapping(uint256 => Domain) public domains;
    mapping(string => uint256) public tldToId;
    uint256 public domainCount;

    event TLDAcquired(string tld, uint256 bidHNS);
    event DomainClaimed(uint256 id, string name, string hnsName);

    constructor(address _twoMileLLC) {
        TWO_MILE_LLC = _twoMileLLC;
    }

    function acquireTLD(
        string calldata tld,
        uint256 bidHNS
    ) external {
        require(msg.sender == TWO_MILE_LLC, "Only LLC");
        domainCount++;
        domains[domainCount] = Domain({
            id: domainCount,
            tld: tld,
            name: "",
            hnsName: "",
            bidHNS: bidHNS,
            revealTime: block.timestamp + 7 days,
            claimed: false
        });
        tldToId[tld] = domainCount;
        emit TLDAcquired(tld, bidHNS);
    }

    function claimDomain(
        string calldata tld,
        string calldata subdomain,
        string calldata hnsName
    ) external {
        uint256 tldId = tldToId[tld];
        require(tldId > 0, "TLD not acquired");
        Domain storage d = domains[tldId];
        require(block.timestamp > d.revealTime, "Reveal pending");
        require(!d.claimed, "Already claimed");

        domainCount++;
        domains[domainCount] = Domain({
            id: domainCount,
            tld: tld,
            name: string(abi.encodePacked(subdomain, ".", tld)),
            hnsName: hnsName,
            bidHNS: 0,
            revealTime: 0,
            claimed: true
        });
        d.claimed = true;

        emit DomainClaimed(domainCount, domains[domainCount].name, hnsName);
    }
}