# fpt_proton_resonance.py
def fpt_resonance(observer, observed):
    coherence = 1.0  # E2EE
    entropy = 0.0    # No scanning
    distance = 1     # Direct peer
    R = coherence * (1 - entropy / (distance ** 2))
    return R

R = fpt_resonance("Jcarroll@proton.me", "LandBackDAO")
print(f"PROTON RESONANCE: {R:.4f}")  # → 1.0000