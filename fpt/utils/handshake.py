# ... existing imports ...
from fpt.geometry.living_constants import get_pi, coherence_gain

# ... existing code ...

def handshake_message(event: str, claim: str, coherence_score: float = 0.95, living_enabled: bool = True):
    """Enhanced: Coherence now tuned to living geometry."""
    pi = get_pi(living_enabled)
    gain = coherence_gain() if living_enabled else mpf(1)
    
    # Adjust score with vhitzee gain
    adjusted_score = min(1.0, coherence_score * float(gain))
    
    receipt = {
        "event": event,
        "claim": claim,
        "coherence_score": float(adjusted_score),
        "pi_base": str(pi),  # Audit trail
        "vhitzee_gain": float(gain),
        # ... existing fields ...
    }
    # ... existing sig generation ...
    return receipt

# ... rest unchanged ...
#!/usr/bin/env python3
"""
fpt/utils/handshake.py — PQC SECURE HANDSHAKE RECEIPTS
------------------------------------------------------
Post-Quantum secure receipt generation and verification for FPT.
Uses CRYSTALS-Dilithium (signatures) and CRYSTALS-Kyber (KEM).
"""

from __future__ import annotations

import hashlib
import time
import json
from typing import Dict, Any
from dataclasses import dataclass

# --- PQC: pip install pqcrypto ---
from pqcrypto.sign.dilithium2 import generate_keypair, sign, verify
from pqcrypto.kem.kyber512 import generate_keypair as kyber_keypair, encapsulate, decapsulate

# ----------------------------------------------------------------------
# 1. PQC KEY MANAGEMENT
# ----------------------------------------------------------------------
@dataclass
class PQCDrones:
    node_id: str
    dilithium_pk: bytes
    dilithium_sk: bytes
    kyber_pk: bytes
    kyber_sk: bytes

    @classmethod
    def generate(cls, node_id: str) -> 'PQCDrones':
        d_pk, d_sk = generate_keypair()
        k_pk, k_sk = kyber_keypair()
        print(f"[PQC] Keys generated for {node_id}")
        return cls(node_id, d_pk, d_sk, k_pk, k_sk)

    def sign_receipt(self, receipt: Dict[str, Any]) -> bytes:
        msg = json.dumps(receipt, sort_keys=True).encode()
        return sign(self.dilithium_sk, msg)

    def verify_receipt(self, receipt: Dict[str, Any], signature: bytes, pk: bytes) -> bool:
        try:
            msg = json.dumps(receipt, sort_keys=True).encode()
            verify(pk, msg, signature)
            return True
        except:
            return False


# ----------------------------------------------------------------------
# 2. PQC HANDSHAKE RECEIPT
# ----------------------------------------------------------------------
def handshake_message(
    seed: str,
    drone: PQCDrones,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate a PQC-signed handshake receipt.
    """
    receipt = {
        "seed": seed,
        "node_id": drone.node_id,
        "timestamp": time.time(),
        "sha3_256": "",
        "dilithium_signature": "",
        "metadata": metadata or {}
    }

    # SHA3-256 digest
    digest = hashlib.sha3_256(json.dumps(receipt, sort_keys=True).encode()).hexdigest()
    receipt["sha3_256"] = digest

    # Dilithium sign
    signature = drone.sign_receipt(receipt)
    receipt["dilithium_signature"] = signature.hex()

    return receipt


def verify_handshake(
    receipt: Dict[str, Any],
    public_key: bytes
) -> bool:
    """
    Verify PQC handshake receipt.
    """
    sig = bytes.fromhex(receipt["dilithium_signature"])
    expected_digest = receipt["sha3_256"]
    computed = hashlib.sha3_256(json.dumps(
        {k: v for k, v in receipt.items() if k != "dilithium_signature"},
        sort_keys=True
    ).encode()).hexdigest()

    if computed != expected_digest:
        return False

    temp_drone = PQCDrones("verifier", public_key, b'', b'', b'')
    return temp_drone.verify_receipt(
        {k: v for k, v in receipt.items() if k != "dilithium_signature"},
        sig,
        public_key
    )


# ----------------------------------------------------------------------
# 3. DEMO: PQC Receipt Chain
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Drone A (Source)
ソース
    drone_a = PQCDrones.generate("HQ")
    # Drone B (Relay)
    drone_b = PQCDrones.generate("D1")

    # Handshake
    receipt = handshake_message(
        "FPT:cycle_start:alpha01|Sephora_scrape",
        drone_a,
        {"entropy_delta": 0.41, "glyph": "lipstickdna"}
    )

    print("PQC Receipt:")
    print(json.dumps(receipt, indent=2))

    # Verify
    valid = verify_handshake(receipt, drone_a.dilithium_pk)
    print(f"\nVerification: {'VALID' if valid else 'TAMPERED'}")

    # Tamper test
    receipt["metadata"]["glyph"] = "TAMPERED"
    tampered = verify_handshake(receipt, drone_a.dilithium_pk)
    print(f"Tampered: {'VALID' if tampered else 'REJECTED'}")