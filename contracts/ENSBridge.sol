// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IENS {
    function setContenthash(bytes32 node, bytes calldata hash) external;
    function setText(bytes32 node, string calldata key, string calldata value) external;
}

contract ENSBridge {
    string public constant BRIDGE_LAW = "The name is dual. The land is one.";
    address public immutable TWO_MILE_LLC;
    string public constant IACA_ID = "2025-DENE-DUAL-001";

    IENS public ens;
    bytes32 public node;

    event NameBridged(string hnsName, string ensName, bytes contenthash);

    constructor(
        address _ens,
        bytes32 _node,
        address _twoMileLLC
    ) {
        ens = IENS(_ens);
        node = _node;
        TWO_MILE_LLC = _twoMileLLC;
    }

    function bridgeToENS(
        string calldata hnsName,
        string calldata ensName,
        bytes calldata contenthash,
        string calldata arweaveTx
    ) external {
        require(msg.sender == TWO_MILE_LLC, "Only LLC");

        // Set IPFS/Arweave contenthash
        ens.setContenthash(node, contenthash);

        // Set metadata
        ens.setText(node, "iaca", IACA_ID);
        ens.setText(node, "hns", hnsName);
        ens.setText(node, "arweave", arweaveTx);
        ens.setText(node, "bridge", "active");

        emit NameBridged(hnsName, ensName, contenthash);
    }

    function verifyBridge() external view returns (bool) {
        return keccak256(ens.text(node, "bridge")) == keccak256("active");
    }
}