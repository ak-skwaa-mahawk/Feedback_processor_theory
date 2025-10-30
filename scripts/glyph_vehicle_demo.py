#!/usr/bin/env python3
# glyph_vehicle_demo.py — AGŁG v101: Live Vote Explanation
from src.glyph_vehicle.core import GlyphVehicle
import numpy as np

# Simulate historical votes
X = np.array([[5000, 85, 60], [10000, 92, 60], [2000, 70, 50]])
y = [0, 1, 0]

vehicle = GlyphVehicle()
vehicle.fit(X, y)

# New motion: Return 10,000 acres
result = vehicle.explain(np.array([[10000, 95, 60]]))
print(f"RESOLUTION: {result['prediction']:.3f}")
print(f"RESONANCE: {result['resonance']:.3f}")
print("GLYPHS:", [g["glyph"] for g in result["glyphs"]])