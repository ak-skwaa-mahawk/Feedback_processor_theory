def recursive_pi(depth=1):
    base_pi = 3.141592653589793
    return base_pi * (1 + (1e-6 * depth))
