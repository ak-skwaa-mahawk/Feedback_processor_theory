"""Scrape Detector module stub for FPT tests."""

import numpy as np

class ScrapeDetector:
    def __init__(self, *args, **kwargs):
        pass

    def detect(self, *args, **kwargs):
        return True

    def compute_entropy(self, x1, x2):
        # Calculate joint or differential entropy approximation
        return float(np.mean(np.abs(x1 - x2)))
