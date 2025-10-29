import numpy as np

class Scrape:
    def __init__(self, energy, distance, entropy, coherence):
        self.energy = energy
        self.distance = distance
        self.entropy = entropy
        self.coherence = coherence

class ScrapeDetector:
    def detect(self, x_orig, x_adv, prediction):
        grad = self.approximate_gradient(x_adv, prediction)
        distance = np.linalg.norm(x_adv - x_orig)
        entropy = self.compute_entropy(x_orig, x_adv)
        energy = np.linalg.norm(grad)
        return Scrape(energy, distance, entropy, coherence=None)

    def compute_entropy(self, x1, x2):
        diff = np.abs(x1 - x2)
        p = diff / np.sum(diff)
        return -np.sum(p * np.log2(p + 1e-9))

    def approximate_gradient(self, x, pred):
        eps = 1e-3
        return (pred(x + eps) - pred(x - eps)) / (2 * eps)

    def boundary_distance(self, pred):
        return np.abs(pred.max() - pred.min())