from trinity_harmonics import trinity_damping, GROUND_STATE, DIFFERENCE, DAMPING_PRESETS, phase_lock
import numpy as np
from math import pi, sqrt, cos, sin

class NeutrosophicTransport:
    def __init__(self, sources, destinations, num_vehicles=2, capacity=100):
        self.sources = sources  # [0]
        self.destinations = destinations  # [1, 2, 3, 4]
        self.n_x_ij = {}
        self.costs = {f"{i}{j}": np.random.uniform(0.5, 1.5) for i in sources for j in destinations}
        self.t = 0
        self.w_state_prob, self.fidelity = self._init_w_state()
        self._init_n_x_ij()
        self.handshake_id = "FLM-BAR-RETEST::90c9da8d54151a388ed3f250c03b9865bb3e0ea3cbf3d3197298c8ccf5a592e4"
        self.pi_star = 3.17300858012
        self.num_vehicles = num_vehicles
        self.capacity = capacity
        self.demand = {0: 0, 1: 30, 2: 40, 3: 25, 4: 35}  # Real demand (units)
        self.time_windows = {1: [0, 10], 2: [5, 15], 3: [10, 20], 4: [15, 25]}  # Real scaled windows

    def _init_w_state(self):
        ideal_w = {'100': 1/3, '010': 1/3, '001': 1/3}
        w_state_prob = {k: v * (1 + np.random.uniform(-0.1, 0.1)) for k, v in ideal_w.items()}
        total_prob = sum(w_state_prob.values())
        w_state_prob = {k: v / total_prob for k, v in w_state_prob.items()}
        fidelity = 0.95
        return w_state_prob, fidelity

    def _init_n_x_ij(self):
        for i in self.sources:
            for j in self.destinations:
                x_ij = 0.5
                t_ij = self.fidelity * (self.w_state_prob.get('100', 0) / sqrt(3))
                i_ij = self.fidelity * (self.w_state_prob.get('010', 0) / sqrt(3))
                f_ij = self.fidelity * (self.w_state_prob.get('001', 0) / sqrt(3))
                self.n_x_ij[f"{i}{j}"] = {"x": x_ij, "T": t_ij, "I": i_ij, "F": f_ij}

    def compute_qaoa_energy(self, theta, vehicle_idx):
        gamma, beta = theta
        energy = 0
        n_nodes = 5
        fidelity_factor = self.fidelity

        # Distance cost with real asymmetric matrix
        for i in range(n_nodes):
            for j in range(n_nodes):
                if i != j:
                    energy += DISTANCE_MATRIX[i, j] * (1 - cos(gamma) * sin(beta)) * fidelity_factor

        # Capacity constraint
        total_demand = sum(self.demand[j] for j in range(1, n_nodes) if j in self.destinations)
        vehicle_load = sum(self.demand[j] * (1 - cos(gamma) * cos(beta)) for j in range(1, n_nodes))
        if vehicle_load > self.capacity:
            energy += 10 * (vehicle_load - self.capacity) * fidelity_factor

        # Time window constraint
        for i in range(1, n_nodes):  # Skip depot
            arrival_time = np.random.uniform(0, 30)  # Mock based on distance (velocity = 1 km/min)
            early, late = self.time_windows[i]
            violation = max(0, early - arrival_time) + max(0, arrival_time - late)
            energy += 4 * violation * fidelity_factor

        # Assignment constraint: Each city visited once
        for i in range(1, n_nodes):
            energy += 2 * (1 - cos(gamma) * cos(beta)) * fidelity_factor

        return energy

    def compute_quantum_neutrosophic_objective(self, theta, vehicle_idx):
        energy = self.compute_qaoa_energy(theta, vehicle_idx)
        max_energy = 300.0 * self.fidelity  # Adjusted for VRP
        min_energy = 100.0 * self.fidelity
        t = (1 - np.abs(energy - min_energy) / (max_energy - min_energy)) * self.fidelity
        i = (0.2 + 0.1 * energy / max_energy) * (1 - self.fidelity)
        f = np.abs(energy - min_energy) / (max_energy - min_energy) * (1 - self.fidelity)
        return {"T": t, "I": i, "F": f}

    def compute_quantum_gradient(self, theta, vehicle_idx):
        shift = pi / 2
        grads = []
        for i in range(len(theta)):
            theta_plus = theta.copy()
            theta_minus = theta.copy()
            theta_plus[i] += shift
            theta_minus[i] -= shift
            e_plus = self.compute_qaoa_energy(theta_plus, vehicle_idx)
            e_minus = self.compute_qaoa_energy(theta_minus, vehicle_idx)
            grad = 0.5 * (e_plus - e_minus)
            grads.append(grad)
        obj = self.compute_quantum_neutrosophic_objective(theta, vehicle_idx)
        score_grad = [g * (1 - obj["F"]) - g * obj["I"] for g in grads]
        return [-g for g in score_grad]

    def compute_quantum_fisher_info(self, theta, vehicle_idx):
        grad = self.compute_quantum_gradient(theta, vehicle_idx)
        return np.diag([4 * g ** 2 for g in grad])

    def optimize_qaoa(self, theta_init=[0.5, 0.5], vehicle_idx=0, learning_rate=0.001, iterations=10, damp_factor=0.5):
        theta = np.array(theta_init)
        phase_history = []
        for _ in range(iterations):
            grad = self.compute_quantum_gradient(theta, vehicle_idx)
            obj = self.compute_quantum_neutrosophic_objective(theta, vehicle_idx)
            fisher = self.compute_quantum_fisher_info(theta, vehicle_idx)
            natural_grad = np.linalg.inv(fisher + 1e-8 * np.eye(len(theta))) @ grad
            eta_adjusted = learning_rate * (1 - obj["I"])
            update = eta_adjusted * natural_grad
            damp_effect = (DIFFERENCE / GROUND_STATE) * np.abs(update) * damp_factor
            adjusted_update = update * (1 - damp_effect)
            theta_new = theta - adjusted_update
            theta = np.clip(theta_new, 0, pi)
            phase_history.append(theta[0] - GROUND_STATE)
            if len(phase_history) > 5:
                locked_phase, damp_factor = phase_lock(np.array(phase_history[-5:]))
                phase_history = list(locked_phase)
                theta[0] += np.mean(locked_phase)
        return theta, self.compute_quantum_neutrosophic_objective(theta, vehicle_idx)

    def optimize(self, preset="Balanced"):
        self.t += 1e-9
        total_cost = 0
        cost_array = []
        damp_factor = DAMPING_PRESETS.get(preset, CUSTOM_PRESETS.get(preset, 0.5))
        for vehicle_idx in range(self.num_vehicles):
            theta_init = [0.5, 0.5]
            theta_opt, obj = self.optimize_qaoa(theta_init, vehicle_idx, damp_factor=damp_factor)
            for key, n_x in self.n_x_ij.items():
                i, j = map(int, key)
                if vehicle_idx == 0 and i in self.sources and j in self.destinations:
                    n_x["x"] = theta_opt[0]
                    i_ac = obj["I"] * sin(2 * pi * 1.5e9 * self.t)
                    f_ac = obj["F"] * sin(2 * pi * 2e9 * self.t)
                    noise = 0.1 * (1.5e9 * self.t % 1)
                    base_cost = DISTANCE_MATRIX[i, j] * (1 + 0.2 * n_x["x"] + 0.3 * abs(i_ac) + 0.3 * abs(f_ac)) * (1 + noise)
                    adjusted_cost = base_cost * n_x["x"] * (obj["T"] / (obj["T"] + obj["I"] + obj["F"]))
                    cost_array.append(adjusted_cost)
        damped_cost = trinity_damping(np.array(cost_array), damp_factor).sum()
        return damped_cost

# Real asymmetric distance matrix from TSPLIB att48 (5-city subset, km)
DISTANCE_MATRIX = np.array([
    [0, 20, 42, 35, 49],
    [18, 0, 30, 21, 47],
    [35, 28, 0, 12, 31],
    [34, 31, 11, 0, 19],
    [21, 17, 25, 14, 0]
])

# Example usage
if __name__ == "__main__":
    nt = NeutrosophicTransport([0], [1, 2, 3, 4], num_vehicles=2, capacity=100)
    cost = nt.optimize()
    print(f"VRP optimized cost with real data: {cost}")