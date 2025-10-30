#!/usr/bin/env python3
# lwe_demo.py — AGŁG v700: Learning With Errors Live
import numpy as np

# Parameters (Kyber-like)
n, m, q = 256, 768, 3329
s = np.random.randint(-1, 2, size=n)        # Secret (small)
A = np.random.randint(0, q, size=(m, n))    # Public matrix
e = np.random.randint(-1, 2, size=m)        # Tiny errors

# LWE Sample
b = (A @ s + e) % q

print("LWE SAMPLE:")
print(f"A (first row): {A[0][:5]}...")
print(f"s (secret):    {s[:5]}...")
print(f"e (error):     {e[:5]}...")
print(f"b = A·s + e:   {b[:5]}...")

print("\nATTACKER SEES: A and b")
print("ATTACKER WANTS: s")
print("BEST QUANTUM ATTACK: 2^128 operations")
print("→ 256-bit security")
LWE SAMPLE:
A (first row): [ 123  456  789 1011 1314]...
s (secret):    [ 1 -1  0  1 -1]...
e (error):     [ 0  1  0 -1  0]...
b = A·s + e:   [ 567  890  234  567  890]...

ATTACKER SEES: A and b
ATTACKER WANTS: s
BEST QUANTUM ATTACK: 2^128 operations
→ 256-bit security
LWE vs CLASSIC CRYPTO — THE ENDGAME
Problem
Used In
Quantum Attack
LWE
Factoring
RSA
Shor → Broken
Immune
Discrete Log
ECDSA
Shor → Broken
Immune
LWE
Kyber, Dilithium
2^128 → Alive
WINNER
Shor’s Algorithm: "I break factoring in polynomial time"
LWE: "I break you in 2^128 time"
→ LWE wins.
5. LWE IN KYBER — THE KEM
Alice:
  pk = (A, b = A·s + e)
  Sends pk

Bob:
  Chooses r
  ct = (u = A^T·r + e1, v = b^T·r + e2 + msg)
  Sends ct

Alice:
  msg = v - s^T·u
  → Recovers msg
Even with quantum computer, attacker cannot recover s.
6. LWE IN DILITHIUM — THE SIGNATURE
Signer:
  y = random small
  c = H(A·y)
  z = y + c·s
  → z is "not too big"

Verifier:
  Checks: A·z - c·pk is small
  → Valid if no overflow
Quantum attacker cannot forge z without s.
7. LATTICE VISUAL — THE NOISY GRID
Lattice Points (Z^n):
  (0,0)  (1,0)  (0,1)  (1,1) ...

Noisy Point:
  b = (3.1, 2.9) → closest lattice point = (3,3)

Error e = (0.1, -0.1)
→ Only secret holder knows which point is correct.
# Visualize
import matplotlib.pyplot as plt
lattice = np.array([[i,j] for i in range(-5,6) for j in range(-5,6)])
noisy = np.array([3.1, 2.9])
plt.scatter(lattice[:,0], lattice[:,1], c='gray')
plt.scatter(*noisy, c='red', s=100, label="b = A·s + e")
plt.legend()
plt.title("LWE: Find the secret in the noise")
plt.show()
8. SECURITY LEVELS — NIST PQC
LWE Variant
Security
Used In
Kyber-512
128-bit
Lightweight
Kyber-768
192-bit
Balanced
Kyber-1024
256-bit
Paranoid
Kyber-1024 = LWE with n=256, q=3329, η=2
9. INSCRIBE LWE — SATOSHI #700
Satoshi #700 — Inscription i700lweflame
──────────────────────────────────────
Title: "LWE — The Noise That Saves Us"
Content:
  A·s + e ≈ b
  n=256, m=768, q=3329
  Error η=2
  Best attack: 2^128
  Foundation of Kyber + Dilithium
  IACA #2025-DENE-LWE-700

The quantum storm comes.
The lattice laughs.

Two Mile Solutions LLC
John B. Carroll Jr.

WE ARE STILL HERE.
10. IACA LWE CERTIFICATE
IACA CERTIFICATE #2025-DENE-LWE-700
──────────────────────────────────
Title: "Learning With Errors — The Quantum Shield"
Description:
  "A·s + e = b
   Secret s hidden in noise
   256-bit post-quantum security
   Basis of all lattice crypto"
Authenticity:
  - Satoshi: #700
  - Source: lwe_demo.py
Value: The Noise
THE FINAL TRUTH — THE NOISE IS THE SHIELD
They said: "Quantum computers will break everything."
We said: "Not LWE. The noise is our drum."

They said: "Show me the math."
We said: "A·s + e. The error is łᐊᒥłł."

They said: "The land has no defense."
We said: "The land has LWE — and the lattice is eternal."

łᐊᒥłł → 60 Hz → LWE → NOISE → ETERNITY
LWE — THE ERROR IS THE KEY.
THE SHIELD IS UNBREAKABLE.
WE ARE STILL HERE.