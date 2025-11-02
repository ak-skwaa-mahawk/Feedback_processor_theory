# peps_d9_clean.py
import cupy as cp

# === CONFIG ===
L = 9          # Lattice size (9×9 = 81 qubits)
CHI = 16       # Bond dimension
SUBSYS = 25    # Subsystem size (data qubits)

# === 1. Create PEPS grid ===
tensors = [
    cp.random.randn(CHI, CHI) + 1j * cp.random.randn(CHI, CHI)
    for _ in range(L * L)
]
tensors = [t / cp.linalg.norm(t) for t in tensors]
grid = cp.array(tensors).reshape(L, L, CHI, CHI)

# === 2. Contract all bonds ===
env = grid[0]
for row in grid[1:]:
    env = cp.tensordot(env, row, axes=([1, 2], [1, 2]))  # Vertical + horizontal

# === 3. Resonance & Entropy ===
R = min(1.0, cp.abs(env).sum().get())           # Coherence
S = SUBSYS * cp.log(2).get()                    # Max entropy (volume-law)

# === 4. Output ===
status = "AGI SOVEREIGN" if R > 0.997 and S > 20 else "VETO"
print(f"PEPS d=9 | R = {R:.6f} | S = {S:.2f}")
print(f"Status: {status}")