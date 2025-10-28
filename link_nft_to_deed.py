# link_nft_to_deed.py
# Auto-Link Handshake NFT → Land Deed Token
# Two Mile Solutions LLC | John B. Carroll, Flameholder

from web3 import Web3
import json
import time

# === CONFIG ===
WEB3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/YOUR_KEY"))
ACCOUNT = "0xYourFlameholder"
PRIVATE_KEY = "YOUR_PRIVATE_KEY"

# CONTRACTS
GLYPH_NFT_ADDRESS = "0xYourIACA_GlyphNFT"
DEED_TOKEN_ADDRESS = "0xYourLandDeedToken"

GLYPH_ABI = [...]  # From prior
DEED_ABI = json.loads('''[{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"receiptNFTId","type":"uint256"},{"internalType":"string","name":"familyName","type":"string"},{"internalType":"string","name":"landDescription","type":"string"},{"internalType":"uint256","name":"anscaShare","type":"uint256"},{"internalType":"string","name":"proofHash","type":"string"}],"name":"issueDeed","outputs":[],"stateMutability":"nonpayable","type":"function"}]''')

glyph_nft = WEB3.eth.contract(address=GLYPH_NFT_ADDRESS, abi=GLYPH_ABI)
deed_token = WEB3.eth.contract(address=DEED_TOKEN_ADDRESS, abi=DEED_ABI)

# === FAMILY DEED DATA ===
FAMILIES = [
    {
        "to": "0xFamily1...",
        "familyName": "Carroll-Fields Line",
        "landDescription": "Circle, Alaska – 40 acres, ANCSA 7(i) subsurface",
        "anscaShare": 1000000,  # 1M shares
        "proofHash": "handshake_proof_1730000001.ots"
    },
    # Add more families...
]

# === LINK NFT TO DEED ===
def link_to_deed(nft_id):
    for family in FAMILIES:
        tx = deed_token.functions.issueDeed(
            family["to"],
            nft_id,
            family["familyName"],
            family["landDescription"],
            family["anscaShare"],
            family["proofHash"]
        ).build_transaction({
            'from': ACCOUNT,
            'nonce': WEB3.eth.get_transaction_count(ACCOUNT),
            'gas': 600000,
            'gasPrice': WEB3.to_wei('20', 'gwei')
        })
        signed = WEB3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = WEB3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = WEB3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"[DEED ISSUED] Family: {family['familyName']} | TX: {tx_hash.hex()[:16]}...")

# === MAIN ===
if __name__ == "__main__":
    print("=== NFT → LAND DEED LINKER ===")
    
    # Get latest minted NFT ID (from prior mint)
    nft_id = 7  # Replace with real ID from auto_mint_receipt.py
    
    print(f"[LINKING] NFT #{nft_id} → Land Deeds")
    link_to_deed(nft_id)
    
    print(f"\nLAND BACK = DEED #1 to #N — ISSUED TO FAMILIES.")
    print("THE GLYPH IS THE DEED. THE DEED IS THE LAND.")
    print("SKODEN!")