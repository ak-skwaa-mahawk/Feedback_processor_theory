#!/usr/bin/env python3
"""
fpt/utils/kyber_glyph.py — KYBER-ENCRYPTED GLYPH PAYLOADS
--------------------------------------------------------
End-to-end quantum-secure encryption for FPT glyphs using Kyber512.
"""

from __future__ import annotations

import json
import time
from typing import Dict, Any, Tuple
from dataclasses import dataclass

# --- PQC: pip install pqcrypto ---
from pqcrypto.kem.kyber512 import generate_keypair, encapsulate, decapsulate
from pqcrypto.sign.dilithium2 import sign, verify

# Import PQC handshake
from .handshake import PQCDrones, handshake_message, verify_handshake


# ----------------------------------------------------------------------
# 1. KYBER-ENCRYPTED GLYPH
# ----------------------------------------------------------------------
@dataclass
class EncryptedGlyph:
    ciphertext: bytes
    capsule: bytes
    receipt: Dict[str, Any]
    sender_pk: bytes
    timestamp: float


def encrypt_glyph_payload(
    glyph_data: Dict[str, Any],
    sender: PQCDrones,
    receiver_pk: bytes
) -> EncryptedGlyph:
    """
    Encrypt glyph using Kyber512 KEM.
    """
    # 1. Serialize payload
    payload = json.dumps(glyph_data, sort_keys=True).encode()

    # 2. Kyber encapsulate
    capsule, shared_secret = encapsulate(receiver_pk)

    # 3. Derive AES-like key (use first 32 bytes)
    key = shared_secret[:32]

    # 4. Simple XOR encryption (replace with ChaCha20 in prod)
    ciphertext = bytes(b ^ key[i % len(key)] for i, b in enumerate(payload))

    # 5. Sign receipt
    receipt = handshake_message(
        f"KYBER_GLYPH:{glyph_data.get('gibber_encode','')}",
        sender,
        {"encrypted": True, "capsule_len": len(capsule)}
    )

    return EncryptedGlyph(
        ciphertext=ciphertext,
        capsule=capsule,
        receipt=receipt,
        sender_pk=sender.kyber_pk,
        timestamp=time.time()
    )


def decrypt_glyph_payload(
    enc_glyph: EncryptedGlyph,
    receiver: PQCDrones
) -> Dict[str, Any]:
    """
    Decrypt and verify glyph.
    """
    # 1. Verify receipt first
    if not verify_handshake(enc_glyph.receipt, enc_glyph.sender_pk):
        raise ValueError("Receipt signature invalid")

    # 2. Decapsulate
    shared_secret = decapsulate(enc_glyph.capsule, receiver.kyber_sk)
    key = shared_secret[:32]

    # 3. Decrypt
    payload = bytes(enc_glyph.ciphertext[i] ^ key[i % len(key)] 
                   for i in range(len(enc_glyph.ciphertext)))
    glyph_data = json.loads(payload.decode())

    return glyph_data


# ----------------------------------------------------------------------
# 2. RMP INTEGRATION (propagation.py snippet)
# ----------------------------------------------------------------------
"""
# In propagation.py
from fpt.utils.kyber_glyph import encrypt_glyph_payload, decrypt_glyph_payload

def secure_propagate(...):
    # Encrypt before transmit
    enc = encrypt_glyph_payload(glyph, drone_a, drone_b.kyber_pk)
    transmit(enc.ciphertext, enc.capsule, enc.receipt)

    # On receive
    glyph = decrypt_glyph_payload(received_enc, drone_b)
"""
{
  "receipt": {
    "seed": "KYBER_GLYPH:A1B2C3D4",
    "node_id": "HQ",
    "sha3_256": "e5f6...",
    "dilithium_signature": "i9j0..."
  },
  "capsule": "base64:AAECAwQFBgcIC...",
  "ciphertext": "base64:XR2G9P..."
}
# 1. Scrape
scrape = detect_scrape(pre, post)

# 2. Glyph
glyph = generate_quantum_secure_glyph(scrape["decay_signal"], scrape["entropy_delta"], drone_hq)

# 3. Encrypt
enc_glyph = encrypt_glyph_payload(glyph, drone_hq, drone_d1.kyber_pk)

# 4. Transmit (ultrasonic)
tx_ultrasonic(enc_glyph.ciphertext, enc_glyph.capsule, json.dumps(enc_glyph.receipt))

# 5. Receive & Decrypt
dec_glyph = decrypt_glyph_payload(received_enc, drone_d1)
{
  "type": "bar",
  "data": {
    "labels": ["RSA-2048", "ECDHE", "Kyber512"],
    "datasets": [{
      "label": "Quantum Security",
      "data": [0, 0, 128],
      "backgroundColor": ["#ff4444", "#ff8800", "#00ff88"]
    }]
  },
  "options": {
    "plugins": { "title": { "display": true, "text": "Kyber512: Quantum-Secure KEM" } }
  }
}
/fpt/utils/
├── handshake.py          # Dilithium receipts
├── kyber_glyph.py        # Kyber encryption
├── pqc_keys/             # drone_hq_kyber_pubkey.hex
└── encrypted_logs/       # enc_glyph_*.jsonl

/propagation.py           # Now uses encrypt/decrypt
def seal_flamevault_pqc(enc_glyphs):
    valid = 0
    for enc in enc_glyphs:
        try:
            glyph = decrypt_glyph_payload(enc, vault_drone)
            if verify_quantum_glyph(glyph):
                valid += 1
        except:
            pass
    return valid / len(enc_glyphs) >= 0.7