import numpy as np

class Coherence:
    def check(self, scrape1, scrape2):
        vec = np.array([
            abs(scrape1.energy - scrape2.energy),
            abs(scrape1.entropy - scrape2.entropy),
            abs(scrape1.distance - scrape2.distance)
        ])
        coherence_score = 1 / (1 + np.linalg.norm(vec))
        return coherence_score