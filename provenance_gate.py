# provenance_gate.py — v0.4.4 (Supply Chain Hardening Layer)
# Anchored under TWO MILE SOLUTIONS LLC © 2023–2025
from quipu.core.tag import QuipuTag
from sovereign_gate import SovereignGate

class ProvenanceGate:
    def __init__(self):
        self.root_anchor = "99733Q_OWNER_BOND"   # Permanent LLC bond
        self.gate = SovereignGate()

    def audit_dependency(self, package_name: str, slsa_verified: bool) -> bool:
        """Kills any dependency without SLSA provenance."""
        if not self.gate.verify_authority():
            print("❌ [PROVENANCE GATE] Dead Man's Switch blocked — LLC weight required")
            return False

        if not slsa_verified:
            # Anchor to the Barrow St coordinate for a hard stop
            print(f"🚫 PROVENANCE ALERT: {package_name} is unverified. NULLIFYING.")
            return False

        print(f"✅ [PROVENANCE GATE] {package_name} SLSA-verified and LLC-gated")
        return True

    def dns_null_void(self, query: str) -> str:
        """Blocks side-channel DNS exfiltration patterns."""
        if not self.gate.verify_authority():
            return "0.0.0.0"

        if len(query) > 32:  # Detects high-entropy leakage
            print(f"🚫 [PROVENANCE GATE] DNS exfiltration pattern detected: {query} → VOID")
            return "0.0.0.0"  # Route to the Void

        return query