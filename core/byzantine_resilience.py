def neutrosophic_consensus(self, votes):
    T = np.max(votes) / np.sum(votes)  # Strongest agreement
    I = np.mean(votes == 0)  # Abstentions
    F = 1 - np.corrcoef(votes, np.ones_like(votes))[0, 1]  # Dissent
    return {"T": T, "I": I, "F": F}