# fpt/nonlinear/feigenbaum_sovereign.py
import numpy as np
import matplotlib.pyplot as plt

def logistic_map(x, r):
    return r * x * (1 - x)

def find_bifurcation_point(r_start, period, steps=10000, tol=1e-8):
    """Find r where period-doubling occurs"""
    x = 0.5
    for _ in range(steps):
        for _ in range(period):
            x = logistic_map(x, r_start)
    
    # Perturb and check divergence
    x1 = x + 1e-8
    for _ in range(period):
        x1 = logistic_map(x1, r_start)
    
    diff = abs(x1 - x)
    if diff > 1e-4:
        return None  # Unstable
    
    # Binary search for onset
    low, high = r_start - 0.1, r_start + 0.1
    for _ in range(50):
        mid = (low + high) / 2
        x = 0.5
        for _ in range(steps):
            for _ in range(period):
                x = logistic_map(x, mid)
        x1 = x + 1e-8
        for _ in range(period):
            x1 = logistic_map(x1, mid)
        if abs(x1 - x) > 1e-4:
            high = mid
        else:
            low = mid
    return mid

# Find bifurcation points
periods = [2, 4, 8, 16, 32, 64, 128]
r_bifurcations = []

print("CROWNING THE FEIGENBAUM SOVEREIGN...")

for p in periods:
    r_guess = 3.0 + (p - 2) * 0.1
    r_bif = find_bifurcation_point(r_guess, p)
    if r_bif:
        r_bifurcations.append(r_bif)
        print(f"Period {p}: r = {r_bif:.10f}")

# Compute Feigenbaum ratios
feigenbaum_ratios = []
for i in range(2, len(r_bifurcations)):
    delta_n = r_bifurcations[i] - r_bifurcations[i-1]
    delta_n1 = r_bifurcations[i-1] - r_bifurcations[i-2]
    ratio = delta_n1 / delta_n
    feigenbaum_ratios.append(ratio)
    print(f"δ_{i} = (r_{i-1} - r_{i-2}) / (r_i - r_{i-1}) = {ratio:.10f}")

# Final estimate
delta_final = np.mean(feigenbaum_ratios[-3:])
print(f"\nFEIGENBAUM CONSTANT δ ≈ {delta_final:.12f}")
print(f"True δ = 4.669201609103...")

# PLOT THE CROWN
plt.figure(figsize=(14, 8), facecolor='black')
plt.gca().set_facecolor('black')

plt.plot(range(3, len(feigenbaum_ratios)+3), feigenbaum_ratios, 'o-', color='cyan', markersize=8, label='Computed δ_n')
plt.axhline(y=4.669201609103, color='gold', linestyle='--', linewidth=2, label='True Feigenbaum δ')

plt.xlabel("Bifurcation Index n", color='white', fontsize=12)
plt.ylabel("Feigenbaum Ratio δ_n", color='white', fontsize=12)
plt.title("FPT FEIGENBAUM SOVEREIGN\nThe Universal Law of Chaos Crowned", color='cyan', fontsize=16, pad=20)

plt.legend(facecolor='black', labelcolor='white')
plt.grid(True, alpha=0.3, color='gray')
plt.tick_params(colors='white')

plt.ylim(4.0, 5.0)
plt.savefig("fpt/nonlinear/feigenbaum_sovereign.png", dpi=300, bbox_inches='tight', facecolor='black')
plt.close()

print("FEIGENBAUM SOVEREIGN CROWNED: fpt/nonlinear/feigenbaum_sovereign.png")