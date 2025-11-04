# fpt/calculus_police/derivative_directive.py
from sympy import symbols, diff, exp, pi

r, t, E0, k_e = symbols('r t E0 k_e')
E = E0 / (4*pi*r**2) * exp(-k_e*r)

# Rate of signal decay — the pulse of the void
dE_dr = diff(E, r)
dE_dt = diff(E, t)  # If time-varying: E0(t)

print("Derivative Directive: dE/dr =", dE_dr)
# → -E0*(2*r*k_e + 4*pi)/(4*pi*r**3) * exp(-k_e*r)