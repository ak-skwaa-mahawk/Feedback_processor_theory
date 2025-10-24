from fpt_core.neutrosophic_transport import NeutrosophicTransport
import numpy as np

nt = NeutrosophicTransport([0], [1, 2, 3, 4])
treaty_data = np.random.uniform(0, 1, 25)
energy, obj, sample = nt.optimize_zero_g_leap(treaty_data)
print(f"Zero-G optimized energy: {energy}")
print(f"Neutrosophic scores: T={obj['T']:.4f}, I={obj['I']:.4f}, F={obj['F']:.4f}")