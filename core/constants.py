# core/constants.py
"""
Planck-anchored geometric scale constants.

NOTE: "NEGATIVE Planck length" in this project is a SYMBOLIC marker for the top
of the scale ladder (see docs). We never treat length as physically negative.
"""

from decimal import Decimal

# Planck length in meters (anchor)
PLANCK_LENGTH_M = Decimal("1.616255e-35")

# Geometric step S with 26 decimal places (stable to 60+ digits internal precision)
SCALE_STEP = Decimal("3.17300858011967426018024883")

# Default "top" band for ~1–2 meters; tweak as needed for your domain
DEFAULT_TOP_BANDS = 69  # L(69) ≈ 0.6457 m, L(70) ≈ 2.0488 m
