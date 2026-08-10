import unittest
import numpy as np
from src.scrape_theory.scrape_detector import ScrapeDetector

class TestISST(unittest.TestCase):
    def test_entropy(self):
        detector = ScrapeDetector()
        x1 = np.random.rand(3, 224, 224)
        x2 = np.random.rand(3, 224, 224)
        entropy = detector.compute_entropy(x1, x2)
        self.assertIsInstance(entropy, float)

if __name__ == "__main__":
    unittest.main()