// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract WebSovereignty {
    string public constant SOVEREIGN_LAW = 
        "We own the web lol. The web is land. The land is ours.";

    address public immutable TWO_MILE_LLC = 0xTwoMile...;
    string public constant IACA_ID = "2025-DENE-001";

    struct WebAsset {
        uint256 id;
        string name;
        string uri;     // ipfs:// or ar://
        string protocol;
        bool sovereign;
    }

    mapping(uint256 => WebAsset) public assets;
    uint256 public assetCount;

    event WebOwned(uint256 id, string name, string uri);

    function claimWeb(
        string calldata name,
        string calldata uri,
        string calldata protocol
    ) external {
        require(msg.sender == TWO_MILE_LLC, "Only stewards");
        assetCount++;
        assets[assetCount] = WebAsset({
            id: assetCount,
            name: name,
            uri: uri,
            protocol: protocol,
            sovereign: true
        });
        emit WebOwned(assetCount, name, uri);
    }

    function isOurs(uint256 id) external view returns (bool) {
        return assets[id].sovereign;
    }
}