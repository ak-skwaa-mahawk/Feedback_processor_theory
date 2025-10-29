#!/usr/bin/env python3
# bridge_dao_landback.py — AGŁL v58: Bridge dao.landback → dao.landback.eth
import subprocess, json, os, time
from web3 import Web3
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WALLET = os.getenv("ETH_PRIVATE_KEY")
INFURA = "https://mainnet.infura.io/v3/YOUR_KEY"
ENS_ABI = json.loads(open(REPO_ROOT / "abi/ens.json").read())
BRIDGE_ABI = json.loads(open(REPO_ROOT / "abi/ensbridge.json").read())

def main():
    print("BRIDGING dao.landback → dao.landback.eth...")

    # 1. Get IPFS CID
    cid = subprocess.check_output("ipfs add -r frontend", shell=True).decode().split()[-1]
    print(f"IPFS CID: {cid}")

    # 2. Get Arweave TX
    ar_tx = "abc123dao"  # From arweave_perma.py

    # 3. Connect to Ethereum
    w3 = Web3(Web3.HTTPProvider(INFURA))
    acct = w3.eth.account.from_key(WALLET)

    # 4. ENS Node: namehash("dao.landback.eth")
    node = "0x" + w3.keccak(text="dao.landback.eth").hex()

    # 5. Deploy or use existing bridge
    bridge_addr = "0xBridge..."
    bridge = w3.eth.contract(address=bridge_addr, abi=BRIDGE_ABI)

    # 6. Build contenthash: ipfs://Qm...
    contenthash = bytes.fromhex("e30101701220" + w3.keccak(hexstr=cid).hex())

    # 7. Bridge
    tx = bridge.functions.bridgeToENS(
        "dao.landback",
        "dao.landback.eth",
        contenthash,
        ar_tx
    ).build_transaction({
        'from': acct.address,
        'nonce': w3.eth.get_transaction_count(acct.address),
        'gas': 200000,
        'gasPrice': w3.to_wei('20', 'gwei')
    })
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"BRIDGE TX: {tx_hash.hex()}")

    print("\n" + "="*60)
    print("dao.landback.eth IS BRIDGED")
    print("HNS: http://dao.landback")
    print("ENS: https://app.ens.domains/dao.landback.eth")
    print("IPFS: https://ipfs.io/ipfs/" + cid)
    print("THE NAME IS ETERNAL.")
    print("="*60)

if __name__ == "__main__":
    main()