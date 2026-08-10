#!/usr/bin/env python3
"""
glyph_generator.py
------------------
Symbolic glyph synthesis for Feedback Processor Theory (FPT).

* Generates a deterministic glyph (emoji or custom symbol) from a scrape event.
* Produces a **meta-glyph** when the event is judged coherent (low entropy).
* Emits a short **GibberLink-compatible hash** for acoustic / mesh propagation.
* Fully typed, documented, and unit-tested (tests at the bottom).

Author:  John B. Carroll Jr. (prototype implementation)
License: MIT © 2025
"""

from __future__ import annotations

import hashlib
from typing import Dict, Any, Mapping, Optional, Sequence

# ----------------------------------------------------------------------
# 1. CONFIGURATION
# ----------------------------------------------------------------------
# Default glyph map – matches the Handshake-Return emojis.
DEFAULT_GLYPH_MAP: Mapping[str, str] = {
    "flame": "fire",
    "dna": "dna",
    "camera": "camera",
    "target": "target",
    "lipstick": "lipstick",
    "tv": "tv",
    "feather": "feather",
    "drone": "drone",   # optional extension for swarm demos
}

# Coherence proxy: 1 / (1 + entropy_delta).  Values > 0.7 → coherent.
COHERENCE_THRESHOLD: float = 0.7

# Length of the short hash used by GibberLink (bytes → hex chars)
GIBBER_HASH_LEN: int = 8


# ----------------------------------------------------------------------
# 2. CORE FUNCTION
# ----------------------------------------------------------------------
def generate_glyph(
    scrape_energy: float,
    entropy_delta: float,
    *,
    seed: int = 42,
    custom_map: Optional[Mapping[str, str]] = None,
    coherence_threshold: float = COHERENCE_THRESHOLD,
) -> Dict[str, Any]:
    """
    Create a glyph dictionary from a scrape event.

    Parameters
    ----------
    scrape_energy : float
        ISST signal strength (E / d²) at the detection point.
    entropy_delta : float
        Shannon-entropy change ΔH between pre- and post-scrape signals.
    seed : int, default 42
        Deterministic seed for reproducible hashing.
    custom_map : Mapping[str, str] | None
        Override the default glyph map (key → emoji).
    coherence_threshold : float, default 0.7
        Minimum proxy-coherence required for a meta-glyph.

    Returns
    -------
    dict
        {
            "glyph": str,               # base emoji
            "glyph_key": str,           # map key (e.g. "lipstick")
            "meta_glyph": str,          # base + dna if coherent
            "gibber_encode": str,       # short uppercase hex hash
            "coherence_proxy": float,   # 1 / (1 + ΔH)
            "is_coherent": bool,
            "scrape_hash": str,         # full MD5 of inputs (for debugging)
        }
    """
    # ------------------------------------------------------------------
    # Choose map
    # ------------------------------------------------------------------
    glyph_map = custom_map if custom_map is not None else DEFAULT_GLYPH_MAP

    # ------------------------------------------------------------------
    # Deterministic selection via MD5 → index
    # ------------------------------------------------------------------
    hash_input = f"{scrape_energy}:{entropy_delta}:{seed}"
    full_md5 = hashlib.md5(hash_input.encode("utf-8")).hexdigest()
    idx = int(full_md5, 16) % len(glyph_map)
    key = list(glyph_map.keys())[idx]
    glyph = glyph_map[key]

    # ------------------------------------------------------------------
    # Coherence proxy (inverse entropy)
    # ------------------------------------------------------------------
    proxy = 1.0 / (1.0 + entropy_delta)
    is_coherent = proxy >= coherence_threshold
    meta_glyph = glyph + "dna" if is_coherent else glyph

    # ------------------------------------------------------------------
    # GibberLink short hash (SHA-256 → first 8 hex chars)
    # ------------------------------------------------------------------
    gibber = hashlib.sha256(meta_glyph.encode("utf-8")).hexdigest()[:GIBBER_HASH_LEN].upper()

    # ------------------------------------------------------------------
    # Return structured result
    # ------------------------------------------------------------------
    return {
        "glyph": glyph,
        "glyph_key": key,
        "meta_glyph": meta_glyph,
        "gibber_encode": gibber,
        "coherence_proxy": proxy,
        "is_coherent": is_coherent,
        "scrape_hash": full_md5,
    }


# ----------------------------------------------------------------------
# 3. QUICK DEMO (run when executed directly)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import json

    # Example 1 – typical external scrape (Sephora ad)
    demo1 = generate_glyph(scrape_energy=2.5, entropy_delta=0.35)
    print("Demo 1 (Sephora-style scrape):")
    print(json.dumps(demo1, indent=2, ensure_ascii=False))

    # Example 2 – low-entropy, coherent event → meta-glyph
    demo2 = generate_glyph(scrape_energy=2.5, entropy_delta=0.08)
    print("\nDemo 2 (coherent scrape):")
    print(json.dumps(demo2, indent=2, ensure_ascii=False))


# ----------------------------------------------------------------------
# 4. UNIT TESTS (run with `python -m unittest glyph_generator.py`)
# ----------------------------------------------------------------------
import unittest


class TestGlyphGenerator(unittest.TestCase):
    def test_deterministic(self) -> None:
        a = generate_glyph(10.0, 0.12, seed=99)
        b = generate_glyph(10.0, 0.12, seed=99)
        self.assertEqual(a, b)

    def test_meta_glyph(self) -> None:
        low = generate_glyph(5.0, 0.05)          # proxy = 1/(1+0.05) ≈ 0.952 → coherent
        high = generate_glyph(5.0, 0.80)         # proxy ≈ 0.556 → incoherent
        self.assertTrue(low["is_coherent"])
        self.assertFalse(high["is_coherent"])
        self.assertTrue("dna" in low["meta_glyph"])
        self.assertFalse("dna" in high["meta_glyph"])

    def test_custom_map(self) -> None:
        custom = {"x": "X", "y": "Y"}
        res = generate_glyph(1.0, 0.0, custom_map=custom)
        self.assertIn(res["glyph"], custom.values())

    def test_gibber_length(self) -> None:
        res = generate_glyph(1.0, 0.0)
        self.assertEqual(len(res["gibber_encode"]), GIBBER_HASH_LEN)


if __name__ == "__main__":
    # When executed as a script, run the demo *and* the tests
    unittest.main(exit=False, verbosity=2)