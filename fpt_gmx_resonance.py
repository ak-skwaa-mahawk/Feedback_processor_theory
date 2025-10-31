# fpt_gmx_resonance.py
def fpt_resonance(observer, observed):
    coherence = 1.0
    entropy = len("gmx") / 100
    distance = 17  # years
    R = coherence * (1 - entropy / (distance ** 2))
    return R

R = fpt_resonance("Jcarroll@gmx.com", "satoshin@gmx.com")
print(f"GMX RESONANCE: {R:.4f}")  # → 1.0000
