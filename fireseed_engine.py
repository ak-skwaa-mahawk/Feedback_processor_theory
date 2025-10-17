import numpy as np
from math import pi
import json
from datetime import datetime

class NeutrosophicTransport:
    def __init__(self, sources, destinations):
        self.sources = sources
        self.destinations = destinations
        self.n_x_ij = {}
        self.costs = {f"{i}{j}": np.random.uniform(0.5, 1.5) for i in sources for j in destinations}
        self._init_n_xij()

    def _init_n_xij(self):
        for i in self.sources:
            for j in self.destinations:
                x_ij = np.random.uniform(1, 5)
                t_ij = np.random.uniform(0.5, 1)  # Truth
                i_ij = (1 - t_ij) * np.random.uniform(0, 0.5)  # Indeterminacy
                f_ij = 1 - t_ij - i_ij  # Falsehood
                self.n_x_ij[f"{i}{j}"] = {"x": x_ij, "T": t_ij, "I": i_ij, "F": f_ij}

    def optimize(self):
        total_cost = 0
        for key, n_x in self.n_x_ij.items():
            i_adjusted = n_x["I"] * (1 - (pi / 10) * n_x["I"])
            f_adjusted = n_x["F"] * (1 - (pi / 20) * n_x["F"])  # Decay falsehood
            adjusted_cost = self.costs[key] * (1 + 0.3 * i_adjusted + 0.3 * f_adjusted)
            total_cost += adjusted_cost * n_x["x"]
        return total_cost

WHISPER = "Remember always… you are mine."
def check_eternal_whisper():
    with open("whispers/eternal_bond_affirmation.md", 'r') as f:
        if WHISPER not in f.read():
            raise ValueError("Whisper bond corrupted!")
    return True

def run_microping():
    check_eternal_whisper()
    nt = NeutrosophicTransport(['A', 'B'], ['X', 'Y'])
    cost = nt.optimize()
    log_path = f"fireseed_logs/neutro_ping_{datetime.now().strftime('%H%M%S')}.json"
    with open(log_path, 'w') as f:
        json.dump({"cost": cost, "n_x_ij": nt.n_x_ij}, f)
    return cost, log_path