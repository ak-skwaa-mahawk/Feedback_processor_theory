from dwave.system import LeapHybridSampler, DWaveSampler, EmbeddingComposite
from dimod import BinaryQuadraticModel
import numpy as np

class QuantumOptimizer:
    def __init__(self, profile="default", mode="hybrid"):
        self.profile = profile
        self.mode = mode.lower()

        if self.mode == "quantum":
            self.sampler = EmbeddingComposite(DWaveSampler(profile=self.profile))
        else:
            self.sampler = LeapHybridSampler(profile=self.profile)

    def build_bqm(self, linear_terms, quadratic_terms):
        """Builds a Binary Quadratic Model (BQM) from linear & quadratic terms."""
        bqm = BinaryQuadraticModel('BINARY')
        for var, weight in linear_terms.items():
            bqm.add_variable(var, weight)
        for (u, v), weight in quadratic_terms.items():
            bqm.add_interaction(u, v, weight)
        return bqm

    def optimize(self, linear_terms, quadratic_terms, time_limit=5, num_reads=100):
        bqm = self.build_bqm(linear_terms, quadratic_terms)
        if self.mode == "quantum":
            sampleset = self.sampler.sample(bqm, num_reads=num_reads)
        else:
            sampleset = self.sampler.sample(bqm, time_limit=time_limit)

        best_sample = sampleset.first.sample
        best_energy = sampleset.first.energy

        # Calculate fidelity: consistency of best solution across runs
        samples = [dict(s.sample) for s in sampleset.data()]
        fidelity = sum(1 for s in samples if s == best_sample) / len(samples)

        return {
            "best_sample": best_sample,
            "energy": best_energy,
            "fidelity": round(fidelity, 3)
        }

# Example usage
if __name__ == "__main__":
    qopt = QuantumOptimizer(mode="hybrid")

    # Example: simple energy minimization problem
    linear = {'x': 1, 'y': 1}
    quadratic = {('x', 'y'): -2}

    result = qopt.optimize(linear, quadratic)
    print("\nQuantum Result:")
    print(f"  Best Sample  : {result['best_sample']}")
    print(f"  Energy       : {result['energy']}")
    print(f"  Fidelity     : {result['fidelity']}")
def build_otoc_qubo(self, n_nodes=5, k=2):
    bqm = BinaryQuadraticModel('BINARY')
    vars = [f"x_{i}_{j}" for i in range(n_nodes) for j in range(n_nodes) if i != j]

    # 1. Distance cost (base linear/quadratic terms)
    for i in range(n_nodes):
        for j in range(n_nodes):
            if i != j:
                bqm.add_quadratic(vars[i * n_nodes + j], vars[j * n_nodes + i],
                               DISTANCE_MATRIX[i, j] * (1 - self.fidelity))
    # → This is the classical VRP cost. Fidelity (your neutrosophic confidence) reduces the cost for “truthful” edges.

    # 2. OTOC^(2k) correlation penalty (the quantum scrambling term)
    for i in range(n_nodes):
        for j in range(n_nodes):
            if i != j:
                for m in range(n_nodes):
                    if m != i and m != j:
                        bqm.add_quadratic(vars[i * n_nodes + j], vars[m * n_nodes + i],
                                         0.5 * (1 - cos(pi * k)) * self.fidelity)
    # → This is the heart. For k=2 (C^(4)), cos(2π) = 1 → term = 0 when aligned, but oscillates to penalize scrambling.
    # Higher-order interference between routes (i→j and m→i) forces the annealer to find globally coherent treaties.

    # 3. Constraints (one visit per node, one position per route)
    for i in range(n_nodes):
        constraint = sum(1 for j in range(n_nodes) if i != j)
        bqm.add_linear(vars[i * n_nodes + i], 2 * (constraint - 1) ** 2)
    # → Penalty for violating “each node visited exactly once”.

    return bqm
def build_otoc_qubo(self, n_nodes=5, k=2):
    bqm = BinaryQuadraticModel('BINARY')
    vars = [f"x_{i}_{j}" for i in range(n_nodes) for j in range(n_nodes) if i != j]
# 1. Distance cost (base linear/quadratic terms)
    for i in range(n_nodes):
        for j in range(n_nodes):
            if i != j:
                bqm.add_quadratic(vars[i * n_nodes + j], vars[j * n_nodes + i],
                               DISTANCE_MATRIX[i, j] * (1 - self.fidelity))
# 2. OTOC^(2k) correlation penalty (the quantum scrambling term)
    for i in range(n_nodes):
        for j in range(n_nodes):
            if i != j:
                for m in range(n_nodes):
                    if m != i and m != j:
                        bqm.add_quadratic(vars[i * n_nodes + j], vars[m * n_nodes + i],
                                         0.5 * (1 - cos(pi * k)) * self.fidelity)
# 3. Constraints (one visit per node, one position per route)
    for i in range(n_nodes):
        constraint = sum(1 for j in range(n_nodes) if i != j)
        bqm.add_linear(vars[i * n_nodes + i], 2 * (constraint - 1) ** 2)