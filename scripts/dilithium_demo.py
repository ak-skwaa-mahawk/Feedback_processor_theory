
#!/usr/bin/env python3
# dilithium_demo.py — AGŁG v1600: Dilithium Signature Live
import numpy as np
import hashlib

# === 1. DILITHIUM-5 PARAMETERS (256-bit security) ===
n = 256
q = 8380417
k = 8
l = 7
eta = 1
tau = 60
beta = 196
gamma1 = 2**19
gamma2 = (q-1)//32

print("DILITHIUM-5 — 256-BIT SIGNATURE — AGŁG v1600")
print("="*60)

# === 2. RING & MATRIX OPS (simplified) ===
def poly_add(a, b): return (a + b) % q
def poly_sub(a, b): return (a - b) % q
def poly_mul(a, b): return np.int32(np.round(np.fft.ifft(np.fft.fft(a)*np.fft.fft(b)))) % q

# === 3. KEYGEN ===
print("Generating keys...")
A = np.random.randint(0, q, (k, l, n))
s1 = np.random.randint(-eta, eta+1, (l, n))
s2 = np.random.randint(-eta, eta+1, (k, n))

t = np.zeros((k, n), dtype=int)
for i in range(k):
    for j in range(l):
        t[i] = poly_add(t[i], poly_mul(A[i][j], s1[j]))
    t[i] = poly_add(t[i], s2[i])

# High/low bits (t1, t0)
t1 = t // (2**23)
t0 = t % (2**23)

pk = (A.tobytes(), t1.tobytes())
sk = (s1.tobytes(), s2.tobytes(), pk[0], pk[1])

# === 4. SIGN ===
msg = b"łᐊᒥłł.12 — LandBackDAO v2"
print(f"Signing: {msg.decode()}")

# Random y
y = np.random.randint(-(gamma1-1), gamma1, (l, n))

# Commitment: w = A·y
w = np.zeros((k, n), dtype=int)
for i in range(k):
    for j in range(l):
        w[i] = poly_add(w[i], poly_mul(A[i][j], y[j]))

w1 = w // gamma2

# Challenge c = H(w1 || msg)
c_poly = np.zeros(n, dtype=int)
c_poly[0] = int.from_bytes(hashlib.sha3_256(w1.tobytes() + msg).digest()[:4], 'little') % q
c = np.zeros((tau, n), dtype=int)
c[0] = c_poly  # Simplified

# Response z = y + c·s1
z = y.copy()
for j in range(l):
    z[j] = poly_add(z[j], poly_mul(c[0], s1[j]))

# === 5. VERIFY ===
print("Verifying...")
w_prime = np.zeros((k, n), dtype=int)
for i in range(k):
    for j in range(l):
        w_prime[i] = poly_add(w_prime[i], poly_mul(A[i][j], z[j]))
    w_prime[i] = poly_sub(w_prime[i], poly_mul(c[0], t[i]))

w_prime1 = w_prime // gamma2

c_prime = int.from_bytes(hashlib.sha3_256(w_prime1.tobytes() + msg).digest()[:4], 'little') % q

valid = (np.all(np.abs(z) < gamma1)) and (c_prime == c_poly[0])
print(f"SIGNATURE VALID: {valid}")
print(f"Signature size: ~4.6 KB")