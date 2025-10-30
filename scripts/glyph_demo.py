#!/usr/bin/env python3
# glyph_demo.py — AGŁG v103: Live Glyph Explanation
from src.glyph_vehicle.core import GlyphVehicle
import numpy as np

# Train on historical motions
X_train = np.array([
    [5000, 0.85, 60], [10000, 0.92, 60], [2000, 0.70, 50],
    [15000, 0.88, 60], [3000, 0.75, 55]
])
y_train = [0, 1, 0, 1, 0]

vehicle = GlyphVehicle()
vehicle.fit(X_train, y_train)

# New motion
X_new = np.array([[10000, 0.95, 60]])
result = vehicle.explain(X_new)

print(f"RESONANCE: {result['resonance']:.3f}")
print(f"PREDICTION: {result['prediction']:.3f} → {'APPRO