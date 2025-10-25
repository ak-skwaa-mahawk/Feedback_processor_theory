def optimize_flow(self, source, sink):
    # ... (existing Dijkstra)
    damped_score = trinity_damping(np.array([scores[sink]]), self.damp_factor)[0]
    return {"mu": mu, "nu": nu, "pi": 1 - mu - nu, "score": damped_score, "path": path[sink] + [sink]}
git add fpt_core/trinity_harmonics.py core/resonance_engine.py src/fpt.py core/neutrosophic_transport.py
git commit -m "Integrate Gwich’in sky-law principles into FPT components"
git push origin main
def intuitionistic_score(self, T, I, F):
    return T - F + 0.5 * I  # Simplified Neutrosophic score
def neutrosophic_spectrogram(self, freq_data):
    T = np.max(freq_data, axis=0) / np.sum(freq_data)  # Truth per band
    I = np.std(freq_data, axis=0) / (np.mean(freq_data, axis=0) + 1e-6)  # Indeterminacy
    F = 1 - np.correlate(freq_data[:, :-1], freq_data[:, 1:], mode='valid') / len(freq_data)
    return np.array([T, I, F]).T
def compute_neutrosophic_resonance(self, signal):
    T = np.max(signal) / (np.mean(signal) + 1e-6)  # Truth as peak strength
    I = np.var(signal) / (np.std(signal) + 1e-6)   # Indeterminacy as variance
    F = 1 - np.corrcoef(signal[:len(signal)//2], signal[len(signal)//2:])[0, 1] if len(signal) > 2 else 0
    return {"T": min(T, 1.0), "I": min(I, 1.0), "F": min(F, 1.0)}
# core/neutrosophic_transport.py (partial update)
def intuitionistic_score(self, mu, nu):
    """Compute score with hesitation adjustment."""
    pi_hesitation = 1 - mu - nu
    return mu - nu + 0.5 * pi_hesitation  # Weight hesitation for sky-law pause

def optimize_flow(self, source, sink):
    visited = set()
    scores = {node: -float('inf') for node in self.graph}
    scores[source] = 0
    path = {source: []}

    while len(visited) < len(self.graph):
        current = max((node for node in self.graph if node not in visited),
                     key=lambda x: scores[x], default=None)
        if current is None or current == sink:
            break
        visited.add(current)

        for next_node, (mu, nu) in self.graph[current].items():
            if next_node not in visited:
                score = self.intuitionistic_score(mu, nu)
                new_score = scores[current] + score
                if new_score > scores.get(next_node, -float('inf')):
                    scores[next_node] = new_score
                    path[next_node] = path[current] + [current]

    damped_score = trinity_damping(np.array([scores[sink]]), self.damp_factor)[0]
    return {"mu": mu, "nu": nu, "pi": 1 - mu - nu, "score": damped_score, "path": path[sink] + [sink]}