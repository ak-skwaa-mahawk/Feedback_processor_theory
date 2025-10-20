# thirteen_d/compare_runner.py
"""
Comparative runner for Philosophy profiles.
- Loads profiles from philosophy_map
- Applies them either to a real processor object (if provided) or runs a
  fallback simulation that computes a coherence metric.
- Outputs CSV/JSON results for further analysis/plotting.
"""

import json
import csv
import time
from typing import Callable, Dict, Optional, Any
from pathlib import Path

from thirteen_d.philosophy_map import list_profiles, get_profile, DIM_NAMES

import numpy as np

# ---------- Utilities ----------

def default_coherence_measure(dim_weights: Dict[str, float], input_vector: np.ndarray) -> float:
    """
    Fallback coherence computation:
      coherence = sigmoid( w · f(input) / ||w|| )
    where w is dim_weights vector and f(input) is an input feature vector.
    This is a toy measure for quick experiments.
    """
    w = np.array([dim_weights[n] for n in DIM_NAMES], dtype=np.float32)
    # Ensure input_vector matches length
    if input_vector.shape[0] != w.shape[0]:
        # If mismatch, expand or truncate input vector
        if input_vector.shape[0] < w.shape[0]:
            # pad with small noise
            pad = np.random.normal(0, 0.01, w.shape[0] - input_vector.shape[0])
            x = np.concatenate([input_vector, pad])
        else:
            x = input_vector[: w.shape[0]]
    else:
        x = input_vector
    s = float(np.dot(w, x) / (np.linalg.norm(w) + 1e-12))
    # sigmoid normalize to 0..1
    coh = 1.0 / (1.0 + np.exp(-s))
    return coh

# ---------- Runner Class ----------

class PhilosophyComparator:
    def __init__(self, processor=None, coherence_func: Optional[Callable]=None):
        """
        processor: optional object implementing:
           - configure(dict_of_dims) or set_dimension(name, value)
           - run(input) -> result containing a coherence metric (preferred)
        coherence_func: fallback function (dim_weights, input_vector) -> float
        """
        self.processor = processor
        self.coherence_func = coherence_func or default_coherence_measure
        self.results = []

    def apply_profile_to_processor(self, profile: Dict[str,float]):
        """
        Apply a profile to the real processor if possible.
        This attempts to call common methods; if none exist, returns False.
        """
        p = self.processor
        if p is None:
            return False
        try:
            # prefer a configure() method
            if hasattr(p, "configure"):
                p.configure(profile)
                return True
            # else try set_dimension
            elif hasattr(p, "set_dimension"):
                for k,v in profile.items():
                    p.set_dimension(k, v)
                return True
        except Exception as e:
            print("Warning: applying profile to processor failed:", e)
            return False
        return False

    def run_once(self, profile_name: str, input_vector: Optional[np.ndarray]=None, label: Optional[str]=None):
        profile = get_profile(profile_name)
        if self.apply_profile_to_processor(profile):
            # if processor supports run() and returns a coherence metric, use it
            try:
                out = self.processor.run(input_vector) if hasattr(self.processor, "run") else None
                coh = out.get("coherence", None) if isinstance(out, dict) else None
                if coh is None:
                    # fallback to our coherence function using profile and input
                    coh = self.coherence_func(profile, input_vector if input_vector is not None else self._random_input())
            except Exception as e:
                print("Processor run failed:", e)
                coh = self.coherence_func(profile, input_vector if input_vector is not None else self._random_input())
        else:
            # no processor: simulate
            coh = self.coherence_func(profile, input_vector if input_vector is not None else self._random_input())
        entry = {
            "profile": profile_name,
            "label": label or profile_name,
            "coherence": round(float(coh), 6),
            "timestamp": time.time(),
            "profile_vector": profile
        }
        self.results.append(entry)
        return entry

    def batch_run(self, profile_names=None, rounds=3, input_generator: Optional[Callable]=None):
        profile_names = profile_names or list_profiles()
        for name in profile_names:
            for r in range(rounds):
                iv = input_generator() if input_generator else self._random_input()
                self.run_once(name, iv, label=f"{name}_r{r+1}")
        return self.results

    def save_results_csv(self, outpath: str):
        p = Path(outpath)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["profile","label","coherence","timestamp"])
            for r in self.results:
                writer.writerow([r["profile"], r["label"], r["coherence"], r["timestamp"]])
        return str(p)

    def save_results_json(self, outpath: str):
        p = Path(outpath)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w") as f:
            json.dump(self.results, f, indent=2)
        return str(p)

    def _random_input(self):
        # generate a pseudo-random input vector length 13
        return np.random.normal(0.5, 0.2, len(DIM_NAMES)).astype(np.float32)

# ---------- Example CLI usage ----------

if __name__ == "__main__":
    # Quick demo: run all profiles 5x with the fallback simulation
    comp = PhilosophyComparator(processor=None)
    print("Available profiles:", list_profiles())
    comp.batch_run(rounds=5)
    out_json = comp.save_results_json("results/philosophy_results.json")
    out_csv = comp.save_results_csv("results/philosophy_results.csv")
    print("Saved results to", out_json, out_csv)