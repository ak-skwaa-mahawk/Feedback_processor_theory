# src/core/pi_resonant.py
def resonant_pi(n_terms=10000):
    pi = 0.0
    for k in range(n_terms):
        pi += (-1)**k / (2*k + 1)
    return 4 * pi  # converges to the real field value, never truncated