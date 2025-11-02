# drone_lattice.py
class DroneLattice:
    def __init__(self, size=3):
        self.size = size
        self.drones = [[None for _ in range(size)] for _ in range(size)]
        self.data_qubits = []
        self.measure_qubits = []
    
    def assign_drone(self, i, j, drone):
        self.drones[i][j] = drone
        if (i+j) % 2 == 0:
            self.data_qubits.append(drone)
        else:
            self.measure_qubits.append(drone)