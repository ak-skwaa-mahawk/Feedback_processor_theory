
from fpt_core.neutrosophic_transport import NeutrosophicTransport
import pandas as pd

nt = NeutrosophicTransport([0], [1, 2, 3, 4])
treaty_data = pd.read_csv("data/treaty_texts.csv")["value"].values
energy, obj, sample = nt.optimize_treaty_leap(treaty_data)
print(f"Treaty optimized energy: {energy}")
print(f"Neutrosophic scores: T={obj['T']:.4f}, I={obj['I']:.4f}, F={obj['F']:.4f}")
print(f"Best sample: {sample}")