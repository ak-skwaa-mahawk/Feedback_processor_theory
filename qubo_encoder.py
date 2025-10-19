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