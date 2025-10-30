#!/usr/bin/env python3
# scripts/glyph_vehicle.py
import numpy as np
from src.glyph_vehicle.core import GlyphVehicle

# Train on historical votes
X = np.array([[5000, 85, 60], [10000, 92, 60], [2000, 70, 50]])
y = [0, 1, 0]

vehicle = GlyphVehicle()
vehicle.fit(X, y)

# New vote
result = vehicle.explain(np.array([[10000, 95, 60]]))
print(result)