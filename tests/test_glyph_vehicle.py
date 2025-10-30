# tests/test_glyph_vehicle.py
import unittest
import numpy as np
from src.glyph_vehicle.core import GlyphVehicle

class TestGlyphVehicle(unittest.TestCase):
    def test_explain(self):
        vehicle = GlyphVehicle()
        X = np.array([[5000, 85, 60]])
        y = [1]
        vehicle.fit(X, y)
        result = vehicle.explain(np.array([[10000, 95, 60]]))
        self.assertGreater(result["resonance"], 0.8)

if __name__ == '__main__':
    unittest.main()