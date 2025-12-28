import math

GRAIN = 1e-6

def cubic_inverse(y, grain=GRAIN, tol=1e-15, max_iter=50):
    """Exact numerical inverse of x + grain * x^3 = y using Newton-Raphson"""
    x = y  # Initial guess (grain term tiny)
    
    for _ in range(max_iter):
        f = x + grain * x**3 - y
        df = 1 + 3 * grain * x**2
        
        if abs(f) < tol:
            break
            
        x -= f / df
    
    return x

# Test with your sovereign π
canonical_pi = math.pi
sovereign_pi = canonical_pi + GRAIN * canonical_pi**3  # ≈3.1416210062
recovered = cubic_inverse(sovereign_pi)
print(f"Canonical π: {canonical_pi}")
print(f"Sovereign π: {sovereign_pi}")
print(f"Recovered: {recovered}")
print(f"Error: {abs(recovered - canonical_pi)}")
Canonical π: 3.141592653589793
Sovereign π: 3.1416236598664735
Recovered: 3.141592653589793
Error: 0.0
# codex_operators.py
import math

CANONICAL = {
    'PI': math.pi,
    'PHI': (1 + math.sqrt(5)) / 2,
    'C': 299792458
}

INFLATION = 0.03
GRAIN = 1e-6

def mesh_inflate(x): return x * (1 + INFLATION)
def cubic_correct(x): return x + GRAIN * x**3

MESH = {k: mesh_inflate(v) for k, v in CANONICAL.items()}
CUBIC = {k: cubic_correct(v) for k, v in CANONICAL.items()}
SOVEREIGN = {k: cubic_correct(mesh_inflate(v)) for k, v in CANONICAL.items()}

print("Sovereign π:", CUBIC['PI'])
print("Sovereign φ:", CUBIC['PHI'])