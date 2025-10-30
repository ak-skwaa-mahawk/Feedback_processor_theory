#!/usr/bin/env python3
# taproot_dilithium.py — AGŁG v1900: Taproot + Dilithium P2TR
import hashlib
import json
from pathlib import Path
from pqclean import Dilithium5

# === 1. DILITHIUM-5 KEYS ===
dil = Dilithium5()
pk, sk = dil.keygen()

print("DILITHIUM-5 KEYS")
print(f"PK: {len(pk)} bytes | SK: {len(sk)} bytes")

# === 2. TAPLEAF: DILITHIUM SCRIPT ===
# Script: OP_PUSH_DILITHIUM_PK OP_DILITHIUM_VERIFY
# Custom opcodes: 0xB0 = DILITHIUM_VERIFY (hypothetical)
tapleaf_script = bytes([0x20 + len(pk)]) + pk + bytes([0xB0])
tapleaf_hash = hashlib.sha256(tapleaf_script).digest()

print(f"TapLeaf Hash: {tapleaf_hash.hex()}")

# === 3. TAPROOT CONSTRUCTION ===
# Internal key (fallback, never used)
internal_key = bytes.fromhex("02" * 32 + "01")  # x-only
internal_pubkey = internal_key[1:]  # 32 bytes

# Merkle root = H(internal_pubkey || tapleaf_hash)
merkle_root = hashlib.tagged_hash("TapBranch", internal_pubkey + tapleaf_hash)

# Output key = internal_pubkey + parity
parity = (internal_key[0] & 1)
output_key = internal_pubkey if parity == 0 else bytes([x ^ 1 for x in internal_pubkey])
p2tr_address = "tb1" + hashlib.new("ripemd160", hashlib.sha256(output_key).digest()).hexdigest()[:60]

print(f"P2TR Address: {p2tr_address[:20]}...")

# === 4. SPENDING: DILITHIUM PATH ===
msg = b"LandBackDAO v2 — Taproot Spend"
sig = dil.sign(msg, sk)

# Control block: c, internal_pubkey, merkle_proof
control_block = bytes([0xc0 | parity]) + internal_pubkey + tapleaf_hash

# Witness stack:
witness = [
    sig,                    # Dilithium signature
    tapleaf_script,         # Script
    control_block           # Merkle proof
]

# === 5. MOCK TX ===
tx = {
    "version": 2,
    "vin": [{
        "txid": "0" * 64,
        "vout": 0,
        "prevout": {
            "scriptpubkey": "5120" + output_key.hex(),
            "value": 100000
        },
        "witness": [item.hex() for item in witness],
        "sequence": 0xffffffff
    }],
    "vout": [{
        "value": 99900,
        "scriptpubkey": "76a914" + "c" * 40 + "88ac"
    }],
    "locktime": 0
}

txid = hashlib.sha256(hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).digest()).digest()[::-1].hex()

# === 6. INSCRIPTION ===
inscription = f"""
TAPROOT + DILITHIUM — AGŁG v1900
────────────────────────────────
P2TR Address: {p2tr_address}
TapLeaf: Dilithium-5 Verify
Sig: {len(sig)} bytes
Control Block: {len(control_block)} bytes
TXID: {txid}
IACA #2025-DENE-TAPROOT-DILITHIUM-1900

The quantum sees a key.
The lattice sees a leaf.
The land is hidden.

Two Mile Solutions LLC
John B. Carroll Jr.

WE ARE STILL HERE.
"""

Path("inscription_taproot_dilithium.txt").write_text(inscription)
print("Inscription: inscription_taproot_dilithium.txt")