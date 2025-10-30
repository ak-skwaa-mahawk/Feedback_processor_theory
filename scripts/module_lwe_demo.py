#!/usr/bin/env python3
# module_lwe_demo.py — AGŁG v1300: Module-LWE in Detail
import numpy as np
import hashlib

# === 1. PARAMETERS (Kyber-512 style, k=2) ===
n, q, k = 256, 3329, 2
eta = 2

print("MODULE-LWE — KYBER-STYLE — AGŁG v1300")
print("="*60)

# === 2. RING MULTIPLICATION (NTT SIMULATED) ===
def ntt_forward(a):
    return np.fft.fft(a)  # Simplified

def ntt_inverse(a):
    return np.fft.ifft(a).real

def ring_mul(a, b, q=q, n=n):
    return np.int32(ntt_inverse(ntt_forward(a) * ntt_forward(b)) + 0.5) % q

# === 3. SAMPLING ===
def sample_small():
    return np.random.randint(-eta, eta+1, size=n)

def sample_uniform(seed):
    h = hashlib.sha3_256(seed).digest()
    return np.frombuffer(h, dtype=np.uint16)[:n] % q

# === 4. KEY GENERATION ===
seed = b"łᐊᒥłł.4 — Module-LWE Keygen"
rho = hashlib.sha512(seed).digest()[:32]

# Public matrix A ∈ R_q^{k×k}
A = np.array([[
    sample_uniform(rho + bytes([i,j]))
    for j in range(k)
] for i in range(k)])

# Secret s, error e
s = np.array([sample_small() for _ in range(k)])
e = np.array([sample_small() for _ in range(k)])

# Public key t = A·s + e
t = np.zeros((k, n), dtype=int)
for i in range(k):
    for j in range(k):
        t[i] = (t[i] + ring_mul(A[i][j], s[j])) % q
    t[i] = (t[i] + e[i]) % q

print(f"Module-LWE Instance (k={k}):")
print(f"A shape: {A.shape} → {k}×{k} polynomials")
print(f"s shape: {s.shape} → {k} small polynomials")
print(f"t = A·s + e: {t.shape}")
print(f"First 5 coeffs of t[0]: {t[0][:5]}")

# === 5. COMPRESSION (Kyber-style) ===
d_t = 10
t_compressed = (t * (2**d_t) // q) % (2**d_t)
print(f"Compressed t: {t_compressed.shape}, {t_compressed.nbytes} bytes")

# === 6. PROOF ===
proof = {
    "type": "Module-LWE",
    "k": k, "n": n, "q": q,
    "t_hash": hashlib.sha256(t_compressed.tobytes()).hexdigest()[:32],
    "iaca": "#2025-DENE-MLWE-1300"
}
print(f"Proof Hash: {proof['t_hash']}")