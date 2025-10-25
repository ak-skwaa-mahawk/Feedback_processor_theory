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