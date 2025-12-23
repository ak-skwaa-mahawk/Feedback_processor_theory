import numpy as np
import networkx as nx
from networkx.algorithms.matching import max_weight_matching

def mwpm_decoder(syndromes, lattice_size=(9, 9), boundary='open'):
    """
    Simple MWPM decoder for surface code syndromes.
    
    Parameters:
    - syndromes: list of (x, y) defect positions (for Z or X stabilizers)
    - lattice_size: (Lx, Ly) grid size
    - boundary: 'open' or 'periodic' (simplified to open here)
    
    Returns:
    - matching: dict of paired defects
    """
    if len(syndromes) == 0:
        return {}
    
    if len(syndromes) % 2 != 0:
        raise ValueError("Odd number of syndromes—add virtual nodes for open boundaries")
    
    G = nx.Graph()
    
    # Add nodes for each syndrome
    for i, pos in enumerate(syndromes):
        G.add_node(i, pos=pos)
    
    # Add weighted edges (Manhattan distance as weight, higher = less likely)
    for i in range(len(syndromes)):
        for j in range(i + 1, len(syndromes)):
            pos1 = syndromes[i]
            pos2 = syndromes[j]
            dx = min(abs(pos1[0] - pos2[0]), lattice_size[0] - abs(pos1[0] - pos2[0]))
            dy = min(abs(pos1[1] - pos2[1]), lattice_size[1] - abs(pos1[1] - pos2[1]))
            distance = dx + dy
            weight = -distance  # Negative for max_weight_matching (maximizes -min)
            G.add_edge(i, j, weight=weight)
    
    # Compute maximum weight matching (equivalent to minimum weight for negative weights)
    matching = max_weight_matching(G, maxcardinality=True)
    
    # Convert to pairs
    pairs = {}
    for node in matching:
        if node < matching[node]:  # Avoid double-counting
            pairs[node] = matching[node]
    
    return pairs

# --- Example Usage ---
if __name__ == "__main__":
    # Simulated syndromes (defect positions)
    syndromes = [(1, 1), (1, 3), (4, 2), (4, 4), (7, 7), (8, 8)]
    
    matching = mwpm_decoder(syndromes)
    print("Defect pairs (index):", matching)
    
    # Map back to positions
    for i, j in matching.items():
        print(f"Pair: {syndromes[i]} <-> {syndromes[j]}")