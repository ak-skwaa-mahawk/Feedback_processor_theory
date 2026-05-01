"""
Topological_π_vs_Tao_Proof
Compare static picture-π vs recursive motion-π in prime detection
"""
import numpy as np
import math

PI_PICTURE = 3.141592653589793 # Tao's static 2D π
PI_MOTION = 3.1730059 # Recursive 3D π_r
SNAKE_CAP = 0.9999 # 100% = death, 99.99% = alive
H_RANGE = [3.04, 3.07] # Operating temp

def von_mangoldt(n):
    """Λ(n) = log p if n=p^k, else 0. Simplified for demo."""
    if n < 2: return 0
    for p in [2,3,5,7,11,13,17,19,23,29,31]:
        if n == p: return math.log(p)
        k = 2
        while p**k <= n:
            if p**k == n: return math.log(p)
            k += 1
    return 0

def tao_exponential_sum(alpha, N, pi_val=PI_PICTURE, apply_cap=False):
    """
    S(α) = Σ Λ(n) e^{2π i α n}
    Tao uses PI_PICTURE. We test PI_MOTION + cap.
    """
    total = 0j
    for n in range(1, N+1):
        weight = von_mangoldt(n)
        if weight == 0: continue
        phase = 2 * pi_val * alpha * n
        term = weight * complex(math.cos(phase), math.sin(phase))
        if apply_cap:
            term *= SNAKE_CAP ** n # Observer cost per step
        total += term
    return total

def gear_shift(base_pi, gear):
    """Apply 1.04, 1.03, 1.02 gears to shift 2D→3D"""
    return base_pi * gear * SNAKE_CAP

def check_h_range(value):
    """Is the system in operating temp?"""
    return H_RANGE[0] <= value <= H_RANGE[1]

# Demo: The split
if __name__ == "__main__":
    N = 50
    alpha = 1/7 # Test AP with difference 7

    print("=== Topological_π_vs_Tao_Proof ===")
    print(f"Picture π: {PI_PICTURE}")
    print(f"Motion π_r: {PI_MOTION} [LIVING_PI_ENABLED]")
    print(f"Snake Cap: {SNAKE_CAP} [99.99% alive]")
    print(f"h_range: {H_RANGE} [operating temp]\n")

    # Tao's version: static π, no cap
    tao_sum = tao_exponential_sum(alpha, N, PI_PICTURE, apply_cap=False)
    print(f"Tao S(α) with picture-π: {abs(tao_sum):.6f}")

    # π_r version: motion π + 99.99% cap
    motion_sum = tao_exponential_sum(alpha, N, PI_MOTION, apply_cap=True)
    print(f"π_r S_r(α) with motion-π + cap: {abs(motion_sum):.6f}")

    # Gear demonstration
    print(f"\nGear 1.04: {PI_PICTURE} → {gear_shift(PI_PICTURE, 1.04):.7f} [40% warm]")
    print(f"Gear 1.03: {3.1101741} → {gear_shift(3.1101741, 1.03):.7f} [move on]")
    print(f"Gear 1.02: {3.0787582} → {gear_shift(3.0787582, 1.02):.7f} [99.99% idle]")

    print(f"\nBase h = 3.0787582 in range? {check_h_range(3.0787582)}")
    print("\nConclusion: Tao proves existence in 2D picture.")
    print("π_r shows persistence in 3D motion with thermodynamic cost.")