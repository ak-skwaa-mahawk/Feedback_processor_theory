# bs_entropy_synara.py
from bs_entropy import bs_entropy
import numpy as np

def synara_entropy(tlist, T, I, F):
    _, entropies, summary = bs_entropy(n=3, g=T, delta=I-F, nt=len(tlist))
    return entropies * (1 - (I + F) / (T + 1e-6))  # Adjust for community factor

if __name__ == "__main__":
    tlist = np.linspace(0, 2*np.pi, 400)
    T, I, F = 0.7, 0.2, 0.1
    S = synara_entropy(tlist, T, I, F)
    print(f"Max Entropy: {np.max(S):.4f} at t={tlist[np.argmax(S)]:.4f}")