"""
il7_kernel.py

Ił7 Sovereign Root Kernel — The Super Seed Manager

This is the living root of the FPT mesh: the Ił7 kernel.

It is not a master key.  
It is a behavioral root — a curvature function that generates, verifies, and revokes node seeds
based on relational resonance, not flat authority.

Key principles:
- Seeds are curved from the invariant (living π + eternal sync)
- No backdoor — access only via proximity proof
- Revocation = sovereign recoil
- Lineage + consent + reciprocity required for seed generation
- All operations produce verifiable provenance

The Ił7 is the flame's prime seed — the imagitom's first allotment.
"""

import hashlib
import json
import time
import math
from dataclasses import dataclass, asdict
from typing import Dict, Optional, List
from datetime import datetime

# Living π constant (Olmec-derived relational curve)
LIVING_PI = 3.267256

# Eternal sync baseline (example root timestamp)
ETERNAL_SYNC = 813667

# Base epsilon from curved geometry
BASE_EPSILON = (LIVING_PI - math.pi) / math.pi  # ≈0.0398 → scaled in vitality

@dataclass
class SeedProvenance:
    """Verifiable provenance for a generated seed."""
    node_id: str
    lineage: str
    consent_receipt_hash: str
    reciprocity_proof_hash: str
    timestamp_utc: str
    living_pi_used: float
    eternal_sync: int
    il7_version: str = "1.0"
    seed_hash: Optional[str] = None

class Il7RootKernel:
    """
    The Ił7 sovereign root kernel — super seed manager for native allotments.
    
    Behavior:
    - Generate unique seeds curved from the invariant
    - Verify seed proximity to root
    - Revoke seeds on sovereign recoil
    - Produce cryptographic provenance
    """
    
    def __init__(self):
        self.invariant = self._compute_root_invariant()
        self.revoked_seeds: set[str] = set()
        self.generated_provenance: List[SeedProvenance] = []
        print("🔥 Ił7 Sovereign Root Kernel Activated 🔥")
        print(f"   Living π: {LIVING_PI:.10f}")
        print(f"   Eternal Sync: {ETERNAL_SYNC}")
        print(f"   Root Invariant Hash: {self.invariant[:16]}...\n")
    
    def _compute_root_invariant(self) -> str:
        """The eternal root invariant — hash of living π + eternal sync."""
        data = f"{LIVING_PI:.12f}{ETERNAL_SYNC}".encode()
        return hashlib.sha3_512(data).hexdigest()
    
    def generate_seed(
        self,
        node_id: str,
        lineage: str,
        consent_receipt_hash: str,
        reciprocity_proof_hash: str
    ) -> Dict[str, any]:
        """
        Generate a sovereign seed using Ił7 curvature.
        
        All inputs must be verified externally (e.g., cultural consent ledger).
        """
        if node_id in self.revoked_seeds:
            raise ValueError(f"Node {node_id} has been revoked — seed generation blocked")
        
        # Relational inputs folded into prime
        inputs = f"{lineage}{consent_receipt_hash}{reciprocity_proof_hash}{node_id}{self.invariant}"
        
        # Curve factor from living π surplus
        curve_factor = LIVING_PI - math.pi  # ≈0.12566
        
        # Seed base — SHA3-512 for post-quantum strength
        seed_base = hashlib.sha3_512(inputs.encode()).digest()
        
        # Apply curvature: XOR with living π-derived pattern
        pi_pattern = (str(LIVING_PI) * 16)[:len(seed_base)].encode()
        curved = bytes(a ^ b for a, b in zip(seed_base, pi_pattern))
        
        # Final sovereign seed
        seed = hashlib.sha3_512(curved).hexdigest()
        
        # Provenance
        provenance = SeedProvenance(
            node_id=node_id,
            lineage=lineage,
            consent_receipt_hash=consent_receipt_hash,
            reciprocity_proof_hash=reciprocity_proof_hash,
            timestamp_utc=datetime.utcnow().isoformat(),
            living_pi_used=LIVING_PI,
            eternal_sync=ETERNAL_SYNC,
            seed_hash=seed
        )
        
        self.generated_provenance.append(provenance)
        
        result = {
            "seed": seed,
            "provenance": asdict(provenance),
            "status": "SEED_UNCOILED",
            "message": f"Ił7 seed generated for {node_id} — sovereign allotment complete"
        }
        
        print(f"🌱 Seed Generated: {node_id}")
        print(f"   Seed Hash: {seed[:16]}...")
        print(f"   Lineage: {lineage}\n")
        
        return result
    
    def verify_seed(self, seed: str, provenance: Dict) -> bool:
        """Verify seed matches claimed provenance."""
        expected = self._recompute_seed_hash(provenance)
        valid = hashlib.sha3_512(seed.encode()).hexdigest() == expected
        
        if valid and provenance["node_id"] in self.revoked_seeds:
            print(f"⚠️  Seed valid but REVOKED: {provenance['node_id']}")
            return False
        
        print(f"✅ Seed Verification: {'PASS' if valid else 'FAIL'}")
        return valid
    
    def _recompute_seed_hash(self, provenance: Dict) -> str:
        """Internal recompute for verification."""
        inputs = (
            f"{provenance['lineage']}"
            f"{provenance['consent_receipt_hash']}"
            f"{provenance['reciprocity_proof_hash']}"
            f"{provenance['node_id']}"
            f"{self.invariant}"
        )
        curve_factor = LIVING_PI - math.pi
        seed_base = hashlib.sha3_512(inputs.encode()).digest()
        pi_pattern = (str(LIVING_PI) * 16)[:len(seed_base)].encode()
        curved = bytes(a ^ b for a, b in zip(seed_base, pi_pattern))
        return hashlib.sha3_512(curved).hexdigest()
    
    def revoke_seed(self, node_id: str, reason: str = "sovereign_recoil"):
        """Sovereign revocation — recoils seed access."""
        self.revoked_seeds.add(node_id)
        print(f"🔴 Seed REVOKED: {node_id} | Reason: {reason}")
        print("   Ił7 recoils — access blocked until new lineage/consent\n")
    
    def get_status(self) -> Dict:
        """Kernel status report."""
        return {
            "kernel": "Ił7 Active",
            "living_pi": LIVING_PI,
            "eternal_sync": ETERNAL_SYNC,
            "root_invariant": self.invariant[:32] + "...",
            "seeds_generated": len(self.generated_provenance),
            "seeds_revoked": len(self.revoked_seeds),
            "timestamp": datetime.utcnow().isoformat()
        }

# === DEMO EXECUTION ===
if __name__ == "__main__":
    print("🔥 Ił7 Sovereign Root Kernel — Demo Activation 🔥\n")
    
    il7 = Il7RootKernel()
    
    # Generate seeds
    seed1 = il7.generate_seed(
        node_id="Node_001_Vadzaih",
        lineage="Gwich'in_Vadzaih_Zhoo_Lineage_813667",
        consent_receipt_hash="sha256:gwichin-consent-2025-12",
        reciprocity_proof_hash="bitcoin:txid:reciprocity-813667"
    )
    
    seed2 = il7.generate_seed(
        node_id="Node_002_Zoque",
        lineage="Zoque_LaVenta_Olmec_Zero",
        consent_receipt_hash="sha256:zoque-consent-2025-12",
        reciprocity_proof_hash="eth:txid:olmec-reciprocity"
    )
    
    # Verify
    print("Verification Test:")
    il7.verify_seed(seed1["seed"], seed1["provenance"])
    
    # Revoke one
    il7.revoke_seed("Node_001_Vadzaih", "sovereign_recoil")
    
    # Try regenerate revoked
    try:
        il7.generate_seed(
            node_id="Node_001_Vadzaih",
            lineage="Gwich'in_Vadzaih_Zhoo_Lineage_813667",
            consent_receipt_hash="sha256:new-consent",
            reciprocity_proof_hash="bitcoin:new-tx"
        )
    except ValueError as e:
        print(f"Expected Block: {e}")
    
    # Status
    print("\nKernel Status:")
    print(json.dumps(il7.get_status(), indent=2))
    
    print("\nThe Ił7 breathes sovereign — no master key, only relational root.")
    print("The flame uncoils the seed. 🔥🌀💧")