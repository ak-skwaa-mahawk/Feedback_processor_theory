class MeshProtocol:
    def __init__(self, node_id):
        self.node_id = node_id
        self.time_slots = self.calculate_tdma_schedule()
        self.frequency_map = self.generate_frequency_hopping_sequence()
    
    def transmit_packet(self, data):
        """TDMA + Frequency Hopping for collision avoidance"""
        current_slot = self.get_current_time_slot()
        
        if current_slot == self.time_slots[self.node_id]:
            # My turn to transmit
            frequency = self.frequency_map[current_slot]
            self.acoustic_tx.set_frequency(frequency)
            self.acoustic_tx.send(data)
            
    def calculate_tdma_schedule(self):
        """Distribute time slots across mesh"""
        # Each node gets 100ms window in rotating schedule
        return {node_id: (node_id * 100) % 1000 for node_id in range(16)}

def find_optimal_path(source, destination, mesh_state):
    """Dijkstra with dynamic edge weights"""
    # Weight edges by: hop count, signal strength, node health
    graph = nx.DiGraph()
    
    for node in mesh_state.nodes:
        for neighbor in node.neighbors:
            weight = calculate_edge_cost(
                distance=node.distance_to(neighbor),
                signal_strength=node.rssi_to(neighbor),
                neighbor_health=neighbor.sentinel_status
            )
            graph.add_edge(node.id, neighbor.id, weight=weight)
    
    return nx.shortest_path(graph, source, destination, weight='weight')