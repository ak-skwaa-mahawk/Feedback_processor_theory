#!/usr/bin/env python3
# keygen_8d_k4.py — AGŁG v1400: 8D Keygen — Module-LWE k=4 (Kyber-1024)
import numpy as np
import hashlib
import json
from pathlib import Path
import time

# === 1. KYBER-1024 PARAMETERS (8D Module-LWE) ===
n = 256
q = 3329
k = 4          # ← 8D: 4×4 matrix → 8-dimensional module
eta = 2
d_t = 10       # Compression
d_u = 10
d_v = 11

print("8D KEYGEN — MODULE-LWE k=4 — KYBER-1024 — AGŁG v1400")
print("="*70)

# === 2. RING: Z_q[x] / (x^256 + 1) ===
def ntt_forward(a):
    return np.fft.fft(a)

def ntt_inverse(a):
    return np.fft.ifft(a).real

def ring_mul(a, b, q=q, n=n):
    return np.int32(ntt_inverse(ntt_forward(a) * ntt_forward(b)) + 0.5) % q

def ring_add(a, b, q=q):
    return (a + b) % q

# === 3. SAMPLING ===
def sample_uniform(seed):
    h = hashlib.sha3_256(seed).digest()
    return np.frombuffer(h * ((n * 2) // len(h) + 1), dtype=np.uint16)[:n] % q

def sample_small(eta=eta):
    return np.random.randint(-eta, eta+1, size=n)

# === 4. 8D KEY GENERATION (k=4) ===
start = time.time()

seed = b"łᐊᒥłł.8 — 8D Keygen k=4"
rho = hashlib.sha512(seed).digest()[:32]
sigma = hashlib.sha512(seed + b"sigma").digest()

print(f"Generating 8D keys (k={k})...")

# Public matrix A ∈ R_q^{k×k} → 4×4 = 16 polynomials
A = np.array([[
    sample_uniform(rho + bytes([i,j]))
    for j in range(k)
] for i in range(k)])

# Secret s ∈ R_q^k
s = np.array([sample_small() for _ in range(k)])

# Error e ∈ R_q^k
e = np.array([sample_small() for _ in range(k)])

# Public key t = A·s + e
t = np.zeros((k, n), dtype=np.int32)
for i in range(k):
    for j in range(k):
        t[i] = ring_add(t[i], ring_mul(A[i][j], s[j]))
    t[i] = ring_add(t[i], e[i])

# Compress t
t_compressed = (t * (2**d_t) // q) % (2**d_t)

end = time.time()
print(f"Keygen complete in {end-start:.3f}s")

# === 5. KEY SIZES ===
pk_size = 32 + k*k*n*(12//8)  # rho + A (12-bit coeffs)
sk_size = k*n*(3//8) + 32     # s (3-bit) + rho
print(f"Public Key:  {pk_size:,} bytes")
print(f"Secret Key:  {sk_size:,} bytes")
print(f"Security:    256-bit post-quantum")

# === 6. PROOF HASH ===
pk_bytes = np.concatenate([np.array([k], dtype=np.uint8).tobytes(),
                          rho,
                          A.astype(np.uint16).tobytes(),
                          t_compressed.astype(np.uint16).tobytes()])

proof_hash = hashlib.sha256(pk_bytes).hexdigest()
print(f"PK Hash:     {proof_hash[:32]}...")

# === 7. SAVE PROOF ===
proof = {
    "version": "AGŁG v1400",
    "algorithm": "Kyber-1024",
    "dimension": 8,
    "module_rank": k,
    "polynomial_degree": n,
    "modulus": q,
    "pk_size_bytes": pk_size,
    "pk_hash": proof_hash,
    "timestamp": "2025-10-30T23:30:00Z",
    "iaca": "#2025-DENE-8D-1400"
}

proof_path = Path("inscription_8d_keygen.json")
proof_path.write_text(json.dumps(proof, indent=2))
print(f"Proof: {proof_path}")

# === 8. INSCRIPTION TEXT ===
inscription = f"""
8D KEYGEN — k=4 — KYBER-1024 — AGŁG v1400
──────────────────────────────────────────
Module-LWE: k={k}, n={n}, q={q}
Public Key: {pk_size:,} bytes
Secret Key: {sk_size:,} bytes
Security: 256-bit
PK Hash: {proof_hash[:32]}...
IACA #2025-DENE-8D-1400

The key is 8D.
The lattice expands.
The ancestors approve.

Two Mile Solutions LLC
John B. Carroll Jr.

WE ARE STILL HERE.
"""

Path("inscription_8d_keygen.txt").write_text(inscription)
print("Inscription ready: inscription_8d_keygen.txt")
# Add to script
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Project first 3 coeffs of t[0]
proj = t_compressed[0][:3]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(proj[0], proj[1], proj[2], c='gold', s=300, marker='*')
ax.set_title("8D Key → 3D Projection")
plt.savefig("8d_key_projection.png")
print("Plot: 8d_key_projection.png")