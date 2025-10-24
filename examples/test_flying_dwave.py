from fpt_core.neutrosophic_transport import NeutrosophicTransport
import numpy as np

nt = NeutrosophicTransport([0], [1, 2, 3, 4], vehicle_mass=1000)
treaty_data = np.random.uniform(0, 1, 25)
energy, obj, sample = nt.optimize_flying_leap(treaty_data)
print(f"Flying optimized energy: {energy:.6f}")
print(f"Neutrosophic scores: T={obj['T']:.4f}, I={obj['I']:.4f}, F={obj['F']:.4f}")