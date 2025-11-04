#!/usr/bin/env python3
"""
glyph_generator.py — QUANTUM-SECURE FPT
---------------------------------------
Post-quantum glyph synthesis with Dilithium signatures.

* Uses CRYSTALS-Dilithium (NIST PQC)
* Signs gibber_encode with drone private key
* Verifies on receive
* Integrates with propagation.py
"""

from __future__ import annotations

import hashlib
from typing import Dict, Any, Optional, Mapping
import numpy as np

# --- PQC: Install via: pip install pqcrypto ---
from pqcrypto.kem.kyber512 import generate_keypair as kyber_keypair, encapsulate, decapsulate
from pqcrypto.sign.dilithium2 import generate_keypair as dilithium_keypair, sign, verify

# ----------------------------------------------------------------------
# 1. CONFIG
# ----------------------------------------------------------------------
DEFAULT_GLYPH_MAP: Mapping[str, str] = {
    "flame": "fire",
    "dna": "dna",
    "camera": "camera",
    "target": "target",
    "lipstick": "lipstick",
    "tv": "tv",
    "feather": "feather",
    "drone": "drone",
}

COHERENCE_THRESHOLD: float = 0.7
GIBBER_LEN: int = 8


# ----------------------------------------------------------------------
# 2. DRONE KEY MANAGEMENT
# ----------------------------------------------------------------------
class QuantumSecureDrone:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.dilithium_pk, self.dilithium_sk = dilithium_keypair()
        self.kyber_pk, self.kyber_sk = kyber_keypair()
        print(f"[PQC] Drone {node_id} keys generated")

    def sign_gibber(self, gibber: str) -> bytes:
        msg = gibber.encode()
        return sign(self.dilithium_sk, msg)

    def verify_gibber(self, gibber: str, signature: bytes, pk: bytes) -> bool:
        try:
            verify(pk, gibber.encode(), signature)
            return True
        except:
            return False

    def encapsulate_secret(self, peer_pk: bytes) -> tuple[bytes, bytes]:
        return encapsulate(peer_pk)


# ----------------------------------------------------------------------
# 3. QUANTUM-SECURE GLYPH GENERATOR
# ----------------------------------------------------------------------
def generate_quantum_secure_glyph(
    scrape_energy: float,
    entropy_delta: float,
    drone: QuantumSecureDrone,
    *,
    seed: int = 42,
    custom_map: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    """
    Generate PQC-signed glyph.
    """
    glyph_map = custom_map or DEFAULT_GLYPH_MAP
    hash_input = f"{scrape_energy:.3f}:{entropy_delta:.3f}:{seed}:{drone.node_id}"
    idx = int(hashlib.sha3_256(hash_input.encode()).hexdigest(), 16) % len(glyph_map)
    key = list(glyph_map.keys())[idx]
    glyph = glyph_map[key]

    # Coherence proxy
    proxy = 1.0 / (1.0 + entropy_delta)
    is_coherent = proxy >= COHERENCE_THRESHOLD
    meta_glyph = glyph + "dna" if is_coherent else glyph

    # Quantum-secure gibber
    gibber_base = hashlib.sha3_256(f"{meta_glyph}{scrape_energy}{time.time()}".encode()).hexdigest()[:GIBBER_LEN].upper()
    signature = drone.sign_gibber(gibber_base)

    return {
        "glyph": glyph,
        "glyph_key": key,
        "meta_glyph": meta_glyph,
        "gibber_encode": gibber_base,
        "pqc_signature": signature.hex(),
        "pqc_public_key": drone.dilithium_pk.hex(),
        "coherence_proxy": proxy,
        "is_coherent": is_coherent,
        "scrape_hash": hashlib.sha3_256(hash_input.encode()).hexdigest(),
        "timestamp": time.time(),
    }


# ----------------------------------------------------------------------
# 4. VERIFICATION ON RECEIVE
# ----------------------------------------------------------------------
def verify_quantum_glyph(glyph_data: Dict[str, Any]) -> bool:
    """
    Verify received glyph using Dilithium.
    """
    try:
        pk = bytes.fromhex(glyph_data["pqc_public_key"])
        sig = bytes.fromhex(glyph_data["pqc_signature"])
        gibber = glyph_data["gibber_encode"]
        return QuantumSecureDrone("verifier").verify_gibber(gibber, sig, pk)
    except:
        return False


# ----------------------------------------------------------------------
# 5. DEMO: Secure Handshake
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import time

    # Drone A (source)
    drone_a = QuantumSecureDrone("HQ")
    # Drone B (receiver)
    drone_b = QuantumSecureDrone("D1")

    # Simulate scrape
    energy = 18.5
    entropy = 0.09

    # Generate signed glyph
    secure_glyph = generate_quantum_secure_glyph(energy, entropy, drone_a)
    print("Generated Quantum-Secure Glyph:")
    print(f"  Meta: {secure_glyph['meta_glyph']}")
    print(f"  Gibber: {secure_glyph['gibber_encode']}")
    print(f"  Sig: {secure_glyph['pqc_signature'][:32]}...")

    # Transmit (simulated)
    received = secure_glyph.copy()

    # Verify on B
    valid = verify_quantum_glyph(received)
    print(f"\nVerification on D1: {'VALID' if valid else 'TAMPERED'}")

    # Tamper test
    received["gibber_encode"] = "TAMPERED"
    valid_tamper = verify_quantum_glyph(received)
    print(f"Tampered Verification: {'VALID' if valid_tamper else 'REJECTED'}")

    # Output: VALID → REJECTED