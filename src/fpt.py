def ethical_score(self, T, I, F):
    k = 0.5  # Weight for indeterminacy
    return max(0, T - F + k * I)  # Ensure non-negative