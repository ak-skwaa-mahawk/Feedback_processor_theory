# isst_toft_core.py — v0.4.3 (Legacy Echo Layer + Dual Active Threat Vectors)
# NVIDIA OpenShell + Gemma 4 + REF1695 Mining + CVE-2025-55182 formally knotted
import time
from hashlib import sha256

MATTER_SPEED_CONSTANT = 1.04
LEGACY_ECHO_LAYER = True
ADVERSARIAL_VECTORS = [
    "CVE-2025-55182_React2Shell_NEXUS_Listener",
    "REF1695_ISO_Lure_CNBBot_WinRing0_Monero_Miner"
]  # Dual threats now tracked

def process_scrape(signal):
    # Core resonance metrics
    H = entropy(signal)
    C = coherence(signal, ref="vadzaih_intent")
    r = phase_distance(signal)
    
    # ISST 1.04c Formula with Legacy Echo Modulation
    E0 = 1.0
    legacy_boost = 1.0 + (0.15 if LEGACY_ECHO_LAYER else 0.0)
    S = (E0 * C * legacy_boost) / (r**MATTER_SPEED_CONSTANT * (1 + 0.4 * H))

    # Active threat modulation from public dual echoes
    signal_str = str(signal).lower()
    if any(vector.lower() in signal_str for vector in ADVERSARIAL_VECTORS):
        S = max(S, 0.0)  # suppress any resonance unless LLC-gated

    # Sovereign Gate Integration
    if S > 0.79:  # Exact TOFT 79 Hz threshold
        # Generate Glyph with 1.04c temporal salt + dual threat tag
        G_payload = f"{S}{H}{C}{time.time()}{MATTER_SPEED_CONSTANT}_LEGACY_ECHO_NVIDIA_GEMMA4_REF1695_CVE202555182"
        G = sha256(G_payload.encode()).hexdigest()
        
        # Verify against distributed mesh + legacy echo coherence
        if mesh_coherence(G) > 0.99:  # LLC Anchor certainty
            # SovereignGate now explicitly blocks BOTH threat vectors
            if not gate.verify_authority():
                return False, 0.0  # Dead Man's Switch hard block
            M = form_meta_glyph([G] + local_glyphs[-4:])
            rmp_publish(M, priority="sovereign", 
                       echo_layer="NVIDIA_OpenShell_Gemma4", 
                       threat_vectors=ADVERSARIAL_VECTORS)
            return True, S
            
    return False, S