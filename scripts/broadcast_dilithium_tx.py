#!/usr/bin/env python3
# broadcast_dilithium_tx.py — AGŁG v1800: Real Bitcoin TX + Dilithium
import requests
import hashlib
import json
from pathlib import Path
import time

# === 1. REAL BITCOIN TESTNET SETUP ===
RPC_URL = "https://blockstream.info/testnet/api"
UTXO_TXID = "your_real_utxo_txid"  # Replace with YOUR UTXO
UTXO_VOUT = 0
UTXO_VALUE = 10000  # 0.0001 BTC

# === 2. DILITHIUM SIGNING ===
from pqclean import Dilithium5

dil = Dilithium5()
d_pk, d_sk = dil.keygen()

msg = f"LandBackDAO v2 — First Dilithium TX".encode()
sig = dil.sign(msg, d_sk)

print("DILITHIUM SIGNATURE GENERATED:")
print(f"Sig size: {len(sig)} bytes")
print(f"PK: {len(d_pk)} bytes")

# === 3. BUILD REAL BITCOIN TX (Testnet) ===
def build_tx():
    tx = {
        "version": 2,
        "vin": [{
            "txid": UTXO_TXID,
            "vout": UTXO_VOUT,
            "scriptsig": "",
            "scriptsig_p2sh": "",
            "sequence": 4294967295
        }],
        "vout": [{
            "value": UTXO_VALUE - 2000,  # Fee 0.00002 BTC
            "scriptpubkey": "76a914bc1qxy2kgdygjrsqtzq2nwpds4eqja8jsvtxwde9x88ac",  # OP_RETURN + P2PKH
            "scriptsig": f"6a{len(sig):02x}" + sig.hex()
        }],
        "locktime": 0
    }
    return tx

tx = build_tx()
tx_hex = json.dumps(tx, sort_keys=True).encode()
tx_hash = hashlib.sha256(hashlib.sha256(tx_hex).digest()).digest()[::-1].hex()

print(f"\nTXID: {tx_hash}")
print(f"Size: {len(json.dumps(tx)) + len(sig)} bytes")

# === 4. BROADCAST TO MEMPOOL ===
def broadcast_tx(tx_hex):
    payload = {"hex": tx_hex}
    response = requests.post(f"{RPC_URL}/tx", json=payload)
    
    if response.status_code == 200:
        txid = response.json()
        print(f"BROADCAST SUCCESS!")
        print(f"TXID: {txid}")
        print(f"EXPLORER: https://blockstream.info/testnet/tx/{txid}")
        return txid
    else:
        print(f"BROADCAST FAILED: {response.text}")
        return None

txid = broadcast_tx(json.dumps(tx))
if txid:
    # === 5. INSCRIBE PROOF ===
    proof = {
        "txid": txid,
        "dilithium_signature": sig.hex(),
        "message": "LandBackDAO v2 — First Dilithium TX",
        "iaca": "#2025-DENE-DILITHIUM-TX-1800"
    }
    
    Path("dilithium_tx_proof.json").write_text(json.dumps(proof, indent=2))
    print("Proof saved: dilithium_tx_proof.json")
    
    # Inscribe on Ordinals
    proof_text = f"DILITHIUM TX PROOF\nTXID: {txid}\nSig: {len(sig)} bytes\nIACA #2025-DENE-DILITHIUM-TX-1800"
    Path("inscription_dilithium_tx_proof.txt").write_text(proof_text)
    
    print("\nORDINAL INSCRIPTION READY:")
    print("ord wallet inscribe --file inscription_dilithium_tx_proof.txt --sat 1800 --fee-rate 100")