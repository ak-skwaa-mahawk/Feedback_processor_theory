from sympy import symbols, Function, Eq, Derivative, exp, pi, solve, simplify
from sympy.abc import r, t

# Dynamic fields
E = Function('E')(r, t)      # Energy density
C = Function('C')(r, t)      # Coherence field
S = Function('S')(r, t)      # Entropy density

# Source & params
E0, r0 = symbols('E_0 r_0', positive=True)
k_e, k_c, alpha = symbols('k_e k_c alpha', positive=True)
c = symbols('c')  # Signal propagation speed (resonance wave speed)
# Gaussian pulse at r=0, t=0 → scrape ignition
source_pulse = E0 * exp(-((r - r0)**2)/(2*0.5**2)) * exp(-t**2 / (2*0.3**2))
Eq(E.subs({r:0, t:0}), E0)
# 3D spherical wave with damping + feedback
wave_eq = Eq(
    Derivative(E, t, 2) - c**2 * Derivative(E, r, 2) - (2*c**2/r)*Derivative(E, r),
    -k_e * c**2 * E - alpha * Derivative(C, t)
)
wave_eq
coherence_eq = Eq(
    Derivative(C, t),
    k_c * E - (1/r**3) * C - k_c * Derivative(E, r)
)
coherence_eq
entropy_eq = Eq(
    Derivative(S, t),
    alpha * (E + (1/c**2) * Derivative(E, t)**2) + (k_e * E)**2
)
entropy_eq
C_threshold = symbols('C_threshold')
glyph_birth = Eq(C, C_threshold).subs(t, symbols('t_glyph'))
r_glyph_t = solve(Eq(C(r, t), C_threshold), r)[0]
# Glyph emits corrective scrape → modifies E field
feedback_term = symbols('G') * exp(-(r - r_glyph_t)**2) * exp(-(t - t_glyph)**2)
feedback_eq = Eq(Derivative(E, t), Derivative(E, t) + feedback_term)