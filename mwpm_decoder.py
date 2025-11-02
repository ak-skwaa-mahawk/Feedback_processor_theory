# mwpm_decoder.py
import networkx as nx

def decode_syndrome(syndrome):
    G = nx.Graph()
    positions = [(0,0), (0,2), (2,0), (2,2)]  # syndrome locations
    
    for i, s in enumerate(syndrome):
        if s == 1:
            G.add_node(i, pos=positions[i])
    
    # Add edges with weights = Manhattan distance
    for i in range(len(syndrome)):
        for j in range(i+1, len(syndrome)):
            if syndrome[i] and syndrome[j]:
                dist = abs(positions[i][0] - positions[j][0]) + abs(positions[i][1] - positions[j][1])
                G.add_edge(i, j, weight=dist)
    
    if len(G.nodes) < 2:
        return None  # no error or uncorrectable
    
    matching = nx.min_weight_matching(G, weight='weight')
    return list(matching)  # error chain