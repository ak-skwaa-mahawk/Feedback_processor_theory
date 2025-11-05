#!/usr/bin/env python3
"""
fpt/utils/aead_glyph.py — CHACHA20-POLY1305 AEAD FOR FPT
-------------------------------------------------------
Authenticated encryption for quantum-secure glyph payloads.
Uses Kyber512 KEM + ChaCha20-Poly1305 AEAD.
"""

from __future__ import annotations

import json
import time
import os
from typing import Dict, Any, Tuple
from dataclasses import dataclass

# --- PQC + Crypto ---
from pqcrypto.kem.kyber512 import encapsulate, decapsulate
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# Import PQC handshake
from .handshake import PQCDrones, handshake_message


# ----------------------------------------------------------------------
# 1. AEAD-ENCRYPTED GLYPH
# ----------------------------------------------------------------------
@dataclass
class AEADGlyph:
    ciphertext: bytes
    nonce: bytes
    tag: bytes
    capsule: bytes
    receipt: Dict[str, Any]
    sender_kyber_pk: bytes
    timestamp: float


def encrypt_glyph_aead(
    glyph_data: Dict[str, Any],
    sender: PQCDrones,
    receiver_kyber_pk: bytes,
    associated_data: bytes = b""
) -> AEADGlyph:
    """
    Encrypt glyph with ChaCha20-Poly1305 using Kyber-derived key.
    """
    # 1. Serialize payload
    payload = json.dumps(glyph_data, sort_keys=True).encode()

    # 2. Kyber encapsulate
    capsule, shared_secret = encapsulate(receiver_kyber_pk)

    # 3. Derive 256-bit encryption key via HKDF
    hkdf = HKDF(
        algorithm=hashes.SHA3_256(),
        length=32,
        salt=None,
        info=b"FPT_AEAD_GLYPH_v1",
    )
    key = hkdf.derive(shared_secret)

    # 4. ChaCha20-Poly1305 encrypt
    chacha = ChaCha20Poly1305(key)
    nonce = os.urandom(12)  # 96-bit nonce
    ct = chacha.encrypt(nonce, payload, associated_data)
    ciphertext, tag = ct[:-16], ct[-16:]

    # 5. PQC receipt
    receipt = handshake_message(
        f"AEAD_GLYPH:{glyph_data.get('gibber_encode','')}",
        sender,
        {
            "encrypted": True,
            "aead": "ChaCha20-Poly1305",
            "capsule_len": len(capsule),
            "nonce_len": len(nonce)
        }
    )

    return AEADGlyph(
        ciphertext=ciphertext,
        nonce=nonce,
        tag=tag,
        capsule=capsule,
        receipt=receipt,
        sender_kyber_pk=sender.kyber_pk,
        timestamp=time.time()
    )


def decrypt_glyph_aead(
    enc_glyph: AEADGlyph,
    receiver: PQCDrones,
    associated_data: bytes = b""
) -> Dict[str, Any]:
    """
    Decrypt and authenticate glyph.
    """
    # 1. Verify receipt
    from .handshake import verify_handshake
    if not verify_handshake(enc_glyph.receipt, enc_glyph.sender_kyber_pk):
        raise ValueError("Receipt signature invalid")

    # 2. Decapsulate
    shared_secret = decapsulate(enc_glyph.capsule, receiver.kyber_sk)

    # 3. Derive key
    hkdf = HKDF(
        algorithm=hashes.SHA3_256(),
        length=32,
        salt=None,
        info=b"FPT_AEAD_GLYPH_v1",
    )
    key = hkdf.derive(shared_secret)

    # 4. Decrypt + verify
    chacha = ChaCha20Poly1305(key)
    try:
        plaintext = chacha.decrypt(
            enc_glyph.nonce,
            enc_glyph.ciphertext + enc_glyph.tag,
            associated_data
        )
    except:
        raise ValueError("AEAD tag invalid — tampering detected")

    return json.loads(plaintext.decode())


# ----------------------------------------------------------------------
# 2. RMP INTEGRATION (propagation.py)
# ----------------------------------------------------------------------
"""
# In propagation.py
from fpt.utils.aead_glyph import encrypt_glyph_aead, decrypt_glyph_aead

def secure_ultrasonic_transmit(enc_glyph):
    # Bundle: ciphertext, nonce, tag, capsule, receipt
    bundle = {
        "ciphertext": enc_glyph.ciphertext.hex(),
        "nonce": enc_glyph.nonce.hex(),
        "tag": enc_glyph.tag.hex(),
        "capsule": enc_glyph.capsule.hex(),
        "receipt": enc_glyph.receipt
    }
    tx_ultrasonic(json.dumps(bundle))
"""
{
  "ciphertext": "1a2b3c...",
  "nonce": "4d5e6f...",
  "tag": "7g8h9i...",
  "capsule": "j0k1l2...",
  "receipt": {
    "seed": "AEAD_GLYPH:A1B2C3D4",
    "node_id": "HQ",
    "sha3_256": "m3n4o5...",
    "dilithium_signature": "p6q7r8..."
  }
}
# 1. Scrape → Glyph
glyph = generate_quantum_secure_glyph(energy, entropy, drone_hq)

# 2. Encrypt with AEAD
enc = encrypt_glyph_aead(
    glyph, drone_hq, drone_d1.kyber_pk,
    associated_data=b"ULTRASONIC_CHANNEL_1"
)

# 3. Transmit
tx_ultrasonic(enc)

# 4. Receive & Decrypt
dec_glyph = decrypt_glyph_aead(received_enc, drone_d1, b"ULTRASONIC_CHANNEL_1")
{
  "type": "bar",
  "data": {
    "labels": ["XOR", "AES-GCM", "ChaCha20-Poly1305"],
    "datasets": [
      {
        "label": "Integrity",
        "data": [0, 1, 1],
        "backgroundColor": "#ff4444"
      },
      {
        "label": "Quantum Safe",
        "data": [0, 0, 1],
        "backgroundColor": "#00ff88"
      }
    ]
  },
  "options": {
    "plugins": { "title": { "display": true, "text": "ChaCha20-Poly1305: AEAD for FPT" } }
  }
}
/fpt/utils/
├── aead_glyph.py         # ChaCha20-Poly1305 + Kyber
├── handshake.py
├── kyber_glyph.py        # Legacy (XOR) → deprecated
└── encrypted_logs/       # aead_glyph_*.jsonl

/propagation.py           # Now uses AEAD
def seal_flamevault_aead(enc_glyphs):
    valid = 0
    for enc in enc_glyphs:
        try:
            glyph = decrypt_glyph_aead(enc, vault_drone)
            if verify_quantum_glyph(glyph):
                valid += 1
        except:
            pass  # Tampered or invalid
    return valid / len(enc_glyphs) >= 0.7