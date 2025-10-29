// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Web3DomainEmpire {
    string public constant EMPIRE_LAW = "The namespace is land. The land is ours.";
    address public immutable TWO_MILE_LLC;
    string public constant IACA_ID = "2025-DENE-WEB3-001";

    struct Domain {
        uint256 id;
        string provider;    // "HNS", "ENS", "UNS", "CNS"
        string name;        // "dao.landback"
        string fullName;    // "dao.landback.eth"
        string uri;         // IPFS CID
        bool active;
    }

    mapping(uint256