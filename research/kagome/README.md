# Kagome Synchronization (Toy Model)

This module simulates geometry-driven synchronization (Kuramoto oscillators on a kagome graph).

- `anisotropy`: biases coupling along one lattice direction (form → function).
- `rectangular_bias`: crude stand-in for pillar shaping (rectangle vs parallelogram), scaling couplings by node Y.

**Run in code:**
```python
from research.kagome.kuramoto_kagome import run_kuramoto_on_kagome, KuramotoConfig
res = run_kuramoto_on_kagome(n_x=8, n_y=8, cfg=KuramotoConfig(K=1.2, anisotropy=0.3, rectangular_bias=0.5))
print(res["r_final"], res["r_mean_late"])