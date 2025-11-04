#!/usr/bin/env python3
"""
scrape_detector.py
------------------
Core ISST-based perturbation detector for Feedback Processor Theory (FPT).

* Takes pre- and post-event signal arrays.
* Computes Shannon entropy ΔH.
* Applies Inverse-Square Scrape Theory (ISST) decay: S = E / d².
* Returns a fully-typed scrape event ready for glyph generation.

Author:  John B. Carroll Jr. (prototype implementation)
License: MIT © 2025
"""

from __future__ import annotations

import numpy as np
from scipy.stats import entropy
from typing import Dict, Any, Optional, Tuple, Union

# ----------------------------------------------------------------------
# 1. CONFIGURATION
# ----------------------------------------------------------------------
DEFAULT_BINS: int = 32                # Histogram bins for entropy
ENTROPY_THRESHOLD: float = 0.12       # ΔH above which a scrape is declared
MIN_ENERGY: float = 0.1               # Floor for decayed signal


# ----------------------------------------------------------------------
# 2. CORE DETECTION FUNCTION
# ----------------------------------------------------------------------
def detect_scrape(
    signal_pre: np.ndarray,
    signal_post: np.ndarray,
    *,
    initial_energy: float = 10.0,
    distance: float = 1.0,
    bins: int = DEFAULT_BINS,
    entropy_threshold: float = ENTROPY_THRESHOLD,
    add_noise_floor: bool = True,
) -> Dict[str, Any]:
    """
    Detect a scrape event using entropy change and ISST decay.

    Parameters
    ----------
    signal_pre : np.ndarray
        Reference signal (stable baseline).
    signal_post : np.ndarray
        Signal after suspected perturbation.
    initial_energy : float, default 10.0
        Starting energy E at d=1 (arbitrary units).
    distance : float, default 1.0
        Effective "information distance" (hops, time, or spatial).
    bins : int, default 32
        Number of histogram bins for entropy calculation.
    entropy_threshold : float, default 0.12
        Minimum ΔH to flag a scrape.
    add_noise_floor : bool, default True
        Add small epsilon to histograms to avoid log(0).

    Returns
    -------
    dict
        {
            "is_scrape": bool,
            "entropy_pre": float,
            "entropy_post": float,
            "entropy_delta": float,
            "decay_signal": float,
            "energy": float,
            "distance": float,
            "timestamp": float (optional),
            "description": str,
        }
    """
    # ------------------------------------------------------------------
    # 1. Validate inputs
    # ------------------------------------------------------------------
    if signal_pre.shape != signal_post.shape:
        raise ValueError("signal_pre and signal_post must have identical shape")
    if len(signal_pre) == 0:
        raise ValueError("Signals cannot be empty")

    # ------------------------------------------------------------------
    # 2. Histogram + Shannon entropy
    # ------------------------------------------------------------------
    eps = 1e-12 if add_noise_floor else 0.0

    hist_pre, _ = np.histogram(signal_pre, bins=bins, density=True)
    hist_post, _ = np.histogram(signal_post, bins=bins, density=True)

    hist_pre = hist_pre + eps
    hist_post = hist_post + eps

    entropy_pre = entropy(hist_pre, base=2)
    entropy_post = entropy(hist_post, base=2)
    entropy_delta = entropy_post - entropy_pre

    # ------------------------------------------------------------------
    # 3. ISST decay: S = E / d²
    # ------------------------------------------------------------------
    decay_signal = max(MIN_ENERGY, initial_energy / (distance ** 2))

    # ------------------------------------------------------------------
    # 4. Scrape decision
    # ------------------------------------------------------------------
    is_scrape = entropy_delta > entropy_threshold

    description = (
        "SCRAPE DETECTED: High entropy shift"
        if is_scrape
        else "Stable feedback loop"
    )

    # ------------------------------------------------------------------
    # 5. Assemble result
    # ------------------------------------------------------------------
    result = {
        "is_scrape": is_scrape,
        "entropy_pre": float(entropy_pre),
        "entropy_post": float(entropy_post),
        "entropy_delta": float(entropy_delta),
        "decay_signal": float(decay_signal),
        "energy": float(initial_energy),
        "distance": float(distance),
        "description": description,
    }

    return result


# ----------------------------------------------------------------------
# 3. CONVENIENCE: From time-series with window
# ----------------------------------------------------------------------
def detect_scrape_window(
    signal: np.ndarray,
    window_size: int,
    idx: int,
    **kwargs,
) -> Dict[str, Any]:
    """
    Detect scrape by comparing a sliding window around `idx`.

    Parameters
    ----------
    signal : np.ndarray
        Full 1D time-series.
    window_size : int
        Size of pre/post window (total 2×window_size).
    idx : int
        Center index of suspected event.
    **kwargs : passed to `detect_scrape`

    Returns
    -------
    dict
        Same format as `detect_scrape`.
    """
    half = window_size // 2
    pre = signal[max(0, idx - half) : idx]
    post = signal[idx : idx + half]

    if len(pre) < 2 or len(post) < 2:
        raise ValueError("Window too small for reliable entropy")

    return detect_scrape(pre, post, **kwargs)


# ----------------------------------------------------------------------
# 4. DEMO (run when executed directly)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Simulate a clean sine wave + sudden noise burst (scrape)
    t = np.linspace(0, 10, 1000)
    clean = np.sin(t)
    noisy = clean.copy()
    noisy[400:600] += 0.8 * np.random.randn(200)  # Scrape event

    # Detect using window
    event = detect_scrape_window(
        noisy,
        window_size=200,
        idx=500,
        initial_energy=12.0,
        distance=1.5,
    )

    print("Scrape Detection Result:")
    for k, v in event.items():
        print(f"  {k}: {v}")

    # Plot
    plt.figure(figsize=(10, 4))
    plt.plot(t, clean, label="Baseline", alpha=0.6)
    plt.plot(t, noisy, label="Observed", color="orange")
    plt.axvspan(t[400], t[600], color="red", alpha=0.2, label="Scrape Zone")
    plt.title("FPT Scrape Detection Demo")
    plt.xlabel("Time")
    plt.ylabel("Signal")
    plt.legend()
    plt.tight_layout()
    plt.show()


# ----------------------------------------------------------------------
# 5. UNIT TESTS
# ----------------------------------------------------------------------
import unittest


class TestScrapeDetector(unittest.TestCase):
    def setUp(self):
        self.clean = np.sin(np.linspace(0, 5, 100))
        self.noisy = self.clean.copy()
        self.noisy[40:60] += 0.7 * np.random.randn(20)

    def test_detect_scrape(self):
        result = detect_scrape(self.clean, self.noisy, initial_energy=8.0, distance=1.0)
        self.assertTrue(result["is_scrape"])
        self.assertGreater(result["entropy_delta"], 0.1)
        self.assertAlmostEqual(result["decay_signal"], 8.0)

    def test_no_scrape(self):
        result = detect_scrape(self.clean, self.clean)
        self.assertFalse(result["is_scrape"])

    def test_window(self):
        full = np.concatenate([self.clean, self.noisy])
        result = detect_scrape_window(full, window_size=50, idx=120)
        self.assertTrue(result["is_scrape"])

    def test_isst_decay(self):
        result = detect_scrape(self.clean, self.noisy, initial_energy=16.0, distance=2.0)
        self.assertAlmostEqual(result["decay_signal"], 4.0)


if __name__ == "__main__":
    unittest.main(exit=False, verbosity=2)