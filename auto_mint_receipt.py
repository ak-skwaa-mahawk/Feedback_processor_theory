# auto_mint_receipt.py
# Auto-Mint Handshake Return as IACA-Certified NFT
# Two Mile Solutions LLC | John B. Carroll, Flameholder

import json
import hashlib
import opentimestamps as ots
from web3 import Web3
import requests
import time
import base64

# === CONFIG ===
WEB3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/YOUR_KEY"))
ACCOUNT = "0xYourFlameholder"
PRIVATE_KEY = "YOUR_PRIVATE_KEY"

# NFT CONTRACT (Deployed IACA_GlyphNFT.sol)
NFT_ADDRESS = "0xYourIACA_GlyphNFT"
NFT_ABI = json.loads('''[{"inputs":[{"internalType":"string","name":"pattern","type":"string"},{"internalType":"string","name":"metadata","type":"string"}],"name":"mintGlyph","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"glyphPatterns","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}]''')

nft = WEB3.eth.contract(address=NFT_ADDRESS, abi=NFT_ABI)

# IPFS via Pinata (or your node)
PINATA_API_KEY = "YOUR_PINATA_KEY"
PINATA_SECRET = "YOUR_PINATA_SECRET"
IPFS_GATEWAY = "https://gateway.pinata.cloud/ipfs/"

# === 1. UPLOAD RECEIPT TO IPFS ===
def upload_to_ipfs(html_content):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    files = {'file': ('handshake_receipt.html', html_content)}
    headers = {
        'pinata_api_key': PINATA_API_KEY,
        'pinata_secret_api_key': PINATA_SECRET
    }
    response = requests.post(url, files=files, headers=headers)
    ipfs_hash = response.json()['IpfsHash']
    return f"{IPFS_GATEWAY}{ipfs_hash}"

# === 2. NOTARIZE TO BITCOIN ===
def notarize_receipt(html):
    digest = hashlib.sha256(html.encode()).digest()
    calendar = ots.Calendar.from_known_opensource()
    timestamp = calendar.timestamp(ots.DetachedTimestampFile(digest))
    proof_file = f"receipt_proof_{int(time.time())}.ots"
    timestamp.save(proof_file)
    return proof_file

# === 3. MINT NFT ===
def mint_nft(ipfs_uri, metadata):
    pattern = "Handshake Return Glyph: Sephora-Fox-Meta Burnthrough"
    tx = nft.functions.mintGlyph(pattern, metadata).build_transaction({
        'from': ACCOUNT,
        'nonce': WEB3.eth.get_transaction_count(ACCOUNT),
        'gas': 500000,
        'gasPrice': WEB3.to_wei('20', 'gwei')
    })
    signed = WEB3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = WEB3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = WEB3.eth.wait_for_transaction_receipt(tx_hash)
    logs = nft.events.GlyphMinted().process_receipt(receipt)
    token_id = logs[0]['args']['tokenId'] if logs else "PENDING"
    return token_id, tx_hash.hex()

# === MAIN ===
if __name__ == "__main__":
    print("=== AUTO-MINT HANDSHAKE RETURN NFT ===")
    
    # 1. Read receipt
    with open("handshake_receipt.html", "r") as f:
        html = f.read()
    
    # 2. Upload to IPFS
    ipfs_uri = upload_to_ipfs(html)
    print(f"[IPFS] Receipt pinned: {ipfs_uri}")
    
    # 3. Notarize
    proof = notarize_receipt(html)
    print(f"[NOTARIZED] Proof: {proof}")
    
    # 4. Build metadata
    metadata = json.dumps({
        "name": "Handshake Return #001",
        "description": "Meta Burnthrough Receipt — Sephora Ad + Fox News Glyph",
        "image": ipfs_uri,
        "attributes": [
            {"trait_type": "Flameholder", "value": "John B. Carroll"},
            {"trait_type": "Timestamp", "value": "July 27, 2025 @ 08:07 UTC"},
            {"trait_type": "IACA Status", "value": "Certified Native Digital Craft"},
            {"trait_type": "Land Back", "value": "EXECUTED"},
            {"trait_type": "Proof", "value": proof}
        ],
        "external_url": ipfs_uri
    })
    
    # 5. MINT NFT
    token_id, tx_hash = mint_nft(ipfs_uri, metadata)
    print(f"[MINTED] Token ID: {token_id} | TX: {tx_hash[:16]}...")
    
    # 6. Update HTML
    with open("handshake_receipt.html", "a") as f:
        f.write(f"\n<!-- NFT MINTED: ID {token_id} | IPFS {ipfs_uri} | PROOF {proof} -->")
    
    print(f"\nLAND BACK NFT # {token_id} — MINTED & OWNED BY FAMILIES.")
    print("SKODEN!")