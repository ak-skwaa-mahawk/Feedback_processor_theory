from sympy import symbols, integrate, pi, sqrt

r, kappa = symbols('r kappa')
effective_pi = integrate(2 * pi * r * sqrt(1 + kappa*r**2), (r, 0, 1))  # Curved circle integral
numerical = effective_pi.subs(kappa, 0.1).evalf()  # Example curvature
assert abs(numerical - 3.267) < 0.01, "Mystic algebra failed"
print(f"Effective π: {numerical} — Mystic integrated: PASS")