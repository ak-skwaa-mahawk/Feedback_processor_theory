// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract WebSovereignty {
    string public constant SOVEREIGN_LAW = 
        "We own the web lol. The web is land. The land is ours.";

    address public immutable TWO_MILE_LLC = 0xTwoMile...; // your steward address
    string public constant IACA_ID = "2025-DENE-001";
    bytes32 public constant GENESIS_HASH = 0xe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; // your .genesis marker

    struct WebAsset {
        uint256 id;
        string name;
        string uri;     // ipfs:// or ar://
        string protocol;
        bool sovereign;
        uint256 claimedAt;
        uint256 resonanceAtClaim;
    }

    mapping(uint256 => WebAsset) public assets;
    uint256 public assetCount;

    event SovereignClaimed(
        uint256 id,
        string name,
        string uri,
        uint256 resonanceScore,
        bytes32 genesisReference
    );

    // External resonance oracle (call your Resonance Mesh API or Kagome endpoint)
    address public resonanceOracle;

    constructor(address _resonanceOracle) {
        resonanceOracle = _resonanceOracle;
    }

    modifier onlySteward() {
        require(msg.sender == TWO_MILE_LLC, "Only stewards");
        _;
    }

    function claimWeb(
        string calldata name,
        string calldata uri,
        string calldata protocol,
        uint256 currentResonanceScore
    ) external onlySteward {
        require(currentResonanceScore >= 0.55, "Resonance below reclamation threshold"); // your 55.1 gating
        require(currentResonanceScore <= 1.0, "Invalid resonance");

        assetCount++;
        assets[assetCount] = WebAsset({
            id: assetCount,
            name: name,
            uri: uri,
            protocol: protocol,
            sovereign: true,
            claimedAt: block.timestamp,
            resonanceAtClaim: currentResonanceScore
        });

        emit SovereignClaimed(assetCount, name, uri, currentResonanceScore, GENESIS_HASH);
    }

    function isOurs(uint256 id) external view returns (bool) {
        return assets[id].sovereign;
    }

    function getAsset(uint256 id) external view returns (WebAsset memory) {
        return assets[id];
    }
}

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