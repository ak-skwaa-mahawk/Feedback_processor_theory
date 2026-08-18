#!/usr/bin/env python3
import hashlib, json, math
from typing import List, Dict, Any

class MerkleTree:
    def __init__(self, leaves: List[str]):
        self.leaves = [hashlib.sha256(l.encode('utf-8')).hexdigest() for l in leaves]
        self.root = self._build_tree(self.leaves)

    def _build_tree(self, level: List[str]) -> str:
        if not level: return hashlib.sha256(b"").hexdigest()
        if len(level) == 1: return level[0]
        nxt = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i+1] if i+1 < len(level) else left
            nxt.append(hashlib.sha256((left + right).encode('utf-8')).hexdigest())
        return self._build_tree(nxt)

class LatticeFeedbackProcessor:
    PI_STATIC: float = math.pi
    PI_3D_COUPLING: float = 3.204423
    TARGET_FREQUENCY_HZ: float = 79.0
    CYCLE_LATENCY_MS: float = 12.658
    PHASE_LOCK_PHI: float = 1.292748
    LYAPUNOV_DECAY: float = -7.683965

    def __init__(self, lattice_dim: int = 4, base_impedance: float = 0.05):
        self.dim = lattice_dim
        self.base_impedance = base_impedance
        self.cycle_count = 0
        self.total_accumulated_slip = 0.0
        self.nodes = [[1.0 + (i * 0.1), 1.0 - (i * 0.05), 0.5 + (i * 0.2)] for i in range(lattice_dim)]

    def step_lattice(self, op_input: List[float]) -> Dict[str, Any]:
        self.cycle_count += 1
        u_norm = math.sqrt(sum(v**2 for v in op_input))
        gamma = self.base_impedance / (1.0 + math.exp(-u_norm))
        slip = sum(abs((self.PI_3D_COUPLING - self.PI_STATIC) * u) for u in op_input)
        self.total_accumulated_slip += slip
        leaves = []

        for idx in range(self.dim):
            norm = math.sqrt(sum(v**2 for v in self.nodes[idx])) + 1e-12
            grad = [math.cos(self.PHASE_LOCK_PHI * norm) * (v / norm) for v in self.nodes[idx]]
            upd = []
            for a in range(3):
                u_i = op_input[a % len(op_input)]
                x_next = (self.nodes[idx][a] + (self.PI_3D_COUPLING * u_i) + grad[a]) * (1.0 - gamma)
                upd.append(x_next * math.exp(self.LYAPUNOV_DECAY * 1e-3))
            self.nodes[idx] = upd
            leaves.append(f"cycle:{self.cycle_count}|node:{idx}|coords:{[round(v, 6) for v in upd]}|slip:{round(slip, 6)}")

        merkle = MerkleTree(leaves)
        return {
            "cycle": self.cycle_count,
            "merkle_root": merkle.root,
            "damping_gamma": round(gamma, 6),
            "step_phase_slip": round(slip, 6),
            "accumulated_slip": round(self.total_accumulated_slip, 6),
            "lattice_nodes": [[round(v, 6) for v in n] for n in self.nodes]
        }

if __name__ == "__main__":
    proc = LatticeFeedbackProcessor(lattice_dim=4)
    for c in range(1, 6):
        m = proc.step_lattice([0.2 * c, 0.1 * c, 0.05 * c])
        print(f"[Cycle {m['cycle']}] Merkle Root: {m['merkle_root']}")
        print(f"  -> Slip: {m['step_phase_slip']:.6f} | Node 0: {m['lattice_nodes'][0]}")
