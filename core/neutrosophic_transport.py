# core/neutrosophic_transport.py
import numpy as np
from trinity_harmonics import trinity_damping

class NeutrosophicTransport:
    def __init__(self, g, d=0.5): self.graph, self.damp_factor, self.t = g, d, 0
    def intuitionistic_score(self, mu, nu): return mu - nu + 0.5 * (1-mu-nu) * (mu/(nu+1e-6))
    def optimize_flow(self, s, e): 
        v, scores, p = set(), {n: -float('inf') for n in self.graph}, {s: []}
        scores[s] = 0
        while len(v) < len(self.graph):
            c = max((n for n in self.graph if n not in v), key=lambda x: scores[x], default=None)
            if c is None or c == e: break
            v.add(c)
            for n, (mu, nu) in self.graph[c].items():
                if n not in v:
                    s = self.intuitionistic_score(mu, nu)
                    if scores[c] + s > scores.get(n, -float('inf')):
                        scores[n], p[n] = scores[c] + s, p[c] + [c]
        return {"mu": mu, "nu": nu, "pi": 1-mu-nu, "score": trinity_damping([scores[e]], self.damp_factor)[0], "path": p[e]+[e]}
    def dynamic_weights(self, t): return 0.5 + 0.1 * np.sin(2 * pi * t)
    def update_telemetry(self, n, mu, nu): 
        self.t += 1
        w = self.dynamic_weights(self.t % 1)
        for nn, (cm, cn) in self.graph[n].items():
            self.graph[n][nn] = (min(1, cm*w), max(0, cn*(1-w)))

if __name__ == "__main__":
    g = {0: {1: (0.8,0.1), 2: (0.7,0.2)}, 1: {2: (0.6,0.3), 3: (0.9,0.05)}, 2: {3: (0.7,0.2)}, 3: {}}
    nt = NeutrosophicTransport(g)
    r = nt.optimize_flow(0, 3)
    print(f"Path={r['path']}, Score={r['score']:.4f}")