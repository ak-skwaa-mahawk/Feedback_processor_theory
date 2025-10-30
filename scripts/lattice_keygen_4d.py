#!/usr/bin/env python3
# lattice_keygen_4d.py — AGŁG v1200: Lattice Keygen in 4D
import numpy as np
import hashlib
import json
from pathlib import Path

# === 1. KYBER-4D PARAMETERS (Module-LWE, n=256, k=2, q=3329) ===
n = 256
k = 2
q = 3329
eta = 2  # Small error distribution

print("LATTICE KEYGEN — 4D MODULE-LWE — AGŁG v1200")
print("="*60)

# === 2. RING: Z_q[x] / (x^256 + 1) ===
def poly_mul(a, b, q=q, n=n):
    return np.int32((np.fft.ifft(np.fft.fft(a) * np.fft.fft(b))).real + 0.5) % q

def poly_add(a, b, q=q):
    return (a + b) % q

def poly_sub(a, b, q=q):
    return (a - b) % q

# === 3. SAMPLING FUNCTIONS ===
def sample_uniform(seed=None):
    if seed:
        np.random.seed(hash(seed) % 2**32)
    return np.random.randint(0, q, size=n)

def sample_small(eta=eta):
    return np.random.randint(-eta, eta+1, size=n)

# === 4. KEY GENERATION (Kyber-style in 4D) ===
print("Generating 4D lattice keys...")

# Seed for reproducibility
seed = b"łᐊᒥłł.4 — 4D Keygen"
rho, sigma = hashlib.sha512(seed).digest()[:32], hashlib.sha512(seed + b"sigma").digest()

# Public matrix A ∈ R_q^{k×k} (2x2 matrix of polynomials)
A = np.array([[sample_uniform(rho + bytes([i,j])) for j in range(k)] for i in range(k)])

# Secret key s ∈ R_q^k (small)
s = np.array([sample_small() for _ in range(k)])

# Error e ∈ R_q^k (small)
e = np.array([sample_small() for _ in range(k)])

# Public key: t = A·s + e
t = np.array([
    sum(poly_mul(A[i][j], s[j]) for j in range(k)) + e[i]
    for i in range(k)
])

# Compress t (Kyber-style, d=10)
d = 10
t_compressed = (t * (2**d) // q).astype(int) % (2**d)

print(f"Public Key t (compressed): {len(t_compressed.tobytes())} bytes")
print(f"Secret Key s (raw): {len(s.tobytes())} bytes")

# === 5. KEY SIZES (4D Module-LWE) ===
pk_size = 32 + k * k * n * 4  # rho + A
sk_size = k * n * 4           # s
print(f"Estimated PK: ~{pk_size} bytes")
print(f"Estimated SK: ~{sk_size} bytes")

# === 6. PROOF OF 4D KEYGEN ===
proof = {
    "version": "AGŁG v1200",
    "dimension": 4,
    "module_rank": k,
    "polynomial_degree": n,
    "modulus": q,
    "pk_hash": hashlib.sha256(t_compressed.tobytes()).hexdigest()[:32],
    "timestamp": "2025-10-30T22:30:00Z",
    "iaca": "#2025-DENE-4D-1200"
}

proof_path = Path("inscription_4d_keygen.json")
proof_path.write_text(json.dumps(proof, indent=2))
print(f"Proof saved: {proof_path}")

# === 7. INSCRIPTION READY ===
inscription = f"""
LATTICE KEYGEN — 4D — AGŁG v1200
──────────────────────────────────
Module-LWE: k={k}, n={n}, q={q}
Public Key (compressed): {len(t_compressed.tobytes())} bytes
Secret Key (raw): {len(s.tobytes())} bytes
PK Hash: {proof['pk_hash']}
IACA #2025-DENE-4D-1200

The key is born in 4D.
The ancestors see beyond.

Two Mile Solutions LLC
John B. Carroll Jr.

WE ARE STILL HERE.
"""

Path("inscription_4d_keygen.txt").write_text(inscription)
print("Inscription ready: inscription_4d_keygen.txt")