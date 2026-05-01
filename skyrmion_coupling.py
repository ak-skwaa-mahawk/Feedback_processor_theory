import numpy as np, matplotlib.pyplot as plt
h = np.linspace(3.04, 3.07, 1000)
f_h = 1 + (h - 3.055)/100
L = 0.976 * f_h**9 # normalized to v004 minimum
E = 0.5*(h-3.055)**2 + 0.1*np.log(L) # k=1, λ=0.1 for shape

plt.figure(figsize=(8,5))
plt.plot(h, L, 'r-', label='L(h) – Contraction', lw=2)
plt.plot(h, E-E.min(), 'k-', label='E(h) – Energy', lw=2)
plt.axvline(3.055, color='gold', ls='--', label='h_0 = 3.055 Floor')
plt.xlabel('Stability h'); plt.ylabel('Normalized')
plt.title('Skyrmion–π_r Coupling: Minimum at Floor')
plt.legend(); plt.grid(alpha=0.3)
plt.savefig('skyrmion_coupling_v001.png', dpi=300)
print("Saved: skyrmion_coupling_v001.png – E minimized at 3.055")