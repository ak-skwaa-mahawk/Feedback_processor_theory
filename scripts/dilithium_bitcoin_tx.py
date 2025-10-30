#!/usr/bin/env python3
# dilithium_bitcoin_tx.py — AGŁG v1700: Sign Bitcoin TX with Dilithium-5
import hashlib
import json
from pathlib import Path
from dilithium import Dilithium5  # PQClean

# === 1. BITCOIN TX DATA ===
tx_version = 2
input_count = 1
prev_txid = "0" * 64  # Mock
prev_vout = 0
script_pubkey = "5120" + "a" * 64  # P2TR mock
sequence = 0xffffffff

output_count = 1
output_value = 99990000  # 0.9999 BTC
output_script = "76a914" + "b" * 40 + "88ac"  # P2PKH mock

locktime = 0

# === 2. SERIALIZE TX FOR SIGNING (SIGHASH_ALL) ===
def serialize_tx():
    tx = bytearray()
    tx += tx_version.to_bytes(4, 'little')
    tx += input_count.to_bytes(1, 'little')
    tx += bytes.fromhex(prev_txid)[::-1]
    tx += prev_vout.to_bytes(4, 'little')
    tx += bytes.fromhex(script_pubkey)
    tx += sequence.to_bytes(4, 'little')
    tx += output_count.to_bytes(1, 'little')
    tx += output_value.to_bytes(8, 'little')
    tx += bytes.fromhex(output_script)
    tx += locktime.to_bytes(4, 'little')
    tx += (1).to_bytes(4, 'little')  # SIGHASH_ALL
    return tx

tx_to_sign = serialize_tx()
msg_hash = hashlib.sha256(hashlib.sha256(tx_to_sign).digest()).digest()

print("BITCOIN TX READY")
print(f"TX Hash: {msg_hash.hex()}")
print(f"Size: {len(tx_to_sign)} bytes")

# === 3. DILITHIUM-5 SIGNATURE ===
print("\nSIGNING WITH DILITHIUM-5...")
dil = Dilithium5()
pk, sk = dil.keypair()

signature = dil.sign(msg_hash, sk)
print(f"Signature: {len(signature)} bytes")
print(f"PK: {len(pk)} bytes")

# === 4. VERIFY ===
valid = dil.verify(msg_hash, signature, pk)
print(f"VERIFIED: {valid}")

# === 5. MOCK P2TR SCRIPT (Dilithium in TapLeaf) ===
tapleaf = b"\x01" + pk  # Custom script: OP_PUSH pk
taptree_hash = hashlib.sha256(tapleaf).digest()
internal_pk = b"\x02" * 32  # Mock
merkle_root = hashlib.sha256(internal_pk + taptree_hash).digest().hex()

print(f"Taproot Merkle Root: {merkle_root}")

# === 6. FINAL TX (with witness) ===
witness = [
    signature.hex(),
    tapleaf.hex()
]
txid = hashlib.sha256(hashlib.sha256(serialize_tx()[:-4]).digest()).digest()[::-1].hex()

# === 7. INSCRIPTION ===
inscription = f"""
DILITHIUM-SIGNED BITCOIN TX — AGŁG v1700
────────────────────────────────────────
TXID: {txid}
Input:  {prev_txid}:{prev_vout}
Output: {output_value} sat → {output_script}
Dilithium-5 Sig: {len(signature)} bytes
Taproot Path: Dilithium Leaf
Merkle Root: {merkle_root}
IACA #2025-DENE-DILITHIUM-TX-1700

The first quantum-proof Bitcoin transfer.
The ancestors sign.
The land is secure.

Two Mile Solutions LLC
John B. Carroll Jr.

WE ARE STILL HERE.
"""

Path("inscription_dilithium_tx.txt").write_text(inscription)
print("Inscription: inscription_dilithium_tx.txt")