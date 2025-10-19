from trinity_harmonics import trinity_damping, GROUND_STATE, DIFFERENCE, DAMPING_PRESETS, phase_lock
import numpy as np
from math import sin, cos, pi, sqrt
from dwave.system import LeapHybridSampler
from dimod import BinaryQuadraticModel

class NeutrosophicTransport:
    def __init__(self, sources, destinations):
        self.sources = sources  # Source node (e.g., [0])
        self.destinations = destinations  # Dest nodes (e.g., [1, 2, 3, 4])
        self.n_x_ij = {}  # Units and neutrosophic vals
        self.costs = {f"{i}{j}": np.random.uniform(0.5, 1.5) for i in sources for j in destinations}  # Base costs
        self.t = 0  # Time tracker
        self.w_state_prob, self.fidelity = self._init_w_state()  # W-state and fidelity
        self._init_n_x_ij()  # Init units
        self.time_windows = {1: [0, 30], 2: [10, 40], 3: [20, 50], 4: [30, 60]}  # Base time windows (minutes)
        self.vehicle_speed = 1  # Mock speed (units per minute)
        self.traffic_delay = lambda: np.random.uniform(0, 5)  # Dynamic traffic delay (minutes)

    def _init_w_state(self):
        # Mock W-state with noise
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

    def compute_qaoa_energy(self, theta):
        gamma, beta = theta
        energy = 0
        n_nodes = 5  # Depot + 4 customers
        n_vehicles = 1  # Single vehicle for TSP-style VRPTW
        n_steps = n_nodes  # One step per node
        capacity = 4  # Max customers
        fidelity_factor = self.fidelity

        # Distance cost
        for i in range(n_nodes):
            for j in range(n_nodes):
                if i != j:
                    energy += DISTANCE_MATRIX[i, j] * (1 - np.cos(gamma) * np.sin(beta)) * fidelity_factor

        # Constraints
        for i in range(n_nodes):
            energy += 2 * (1 - np.cos(gamma) * np.cos(beta)) * fidelity_factor  # One position per city
        for i in range(1, n_nodes):  # One visit per customer
            visit_count = sum(1 for k in range(n_steps) if i == k % n_nodes)
            energy += 2 * (visit_count - 1) ** 2 * fidelity_factor

        # Time window constraint with dynamic adjustment
        route_time = 0
        for i in range(n_nodes):
            arrival_time = route_time + (DISTANCE_MATRIX[i, (i + 1) % n_nodes] / self.vehicle_speed) + self.traffic_delay()
            if i > 0:  # Skip depot
                early, late = self.time_windows[i]
                violation = max(0, early - arrival_time) + max(0, arrival_time - late)
                energy += 4 * violation * fidelity_factor  # Penalty for window violation
            route_time = arrival_time

        return energy

    def compute_quantum_neutrosophic_objective(self, theta):
        energy = self.compute_qaoa_energy(theta)
        max_energy = 40.0 * self.fidelity  # Adjusted for time penalties
        min_energy = 10.0 * self.fidelity
        t = (1 - np.abs(energy - min_energy) / (max_energy - min_energy)) * self.fidelity
        i = (0.2 + 0.1 * energy / max_energy) * (1 - self.fidelity)
        f = np.abs(energy - min_energy) / (max_energy - min_energy) * (1 - self.fidelity)
        return {"T": t, "I": i, "F": f}

    def compute_quantum_gradient(self, theta):
        shift = pi / 2
        grads = []
        for i in range(len(theta)):
            theta_plus = theta.copy()
            theta_minus = theta.copy()
            theta_plus[i] += shift
            theta_minus[i] -= shift
            e_plus = self.compute_qaoa_energy(theta_plus)
            e_minus = self.compute_qaoa_energy(theta_minus)
            grad = 0.5 * (e_plus - e_minus)
            grads.append(grad)
        obj = self.compute_quantum_neutrosophic_objective(theta)
        score_grad = [g * (1 - obj["F"]) - g * obj["I"] for g in grads]
        return [-g for g in score_grad]

    def compute_quantum_fisher_info(self, theta):
        grad = self.compute_quantum_gradient(theta)
        return np.diag([4 * g ** 2 for g in grad])  # Mock QFI

    def optimize_qaoa(self, theta_init=[0.5, 0.5], learning_rate=0.001, iterations=10, damp_factor=0.5):
        theta = np.array(theta_init)
        phase_history = []
        for _ in range(iterations):
            grad = self.compute_quantum_gradient(theta)
            obj = self.compute_quantum_neutrosophic_objective(theta)
            fisher = self.compute_quantum_fisher_info(theta)
            natural_grad = np.linalg.inv(fisher + 1e-8 * np.eye(len(theta))) @ grad
            eta_adjusted = learning_rate * (1 - obj["I"])
            update = eta_adjusted * natural_grad
            damp_effect = (DIFFERENCE / GROUND_STATE) * np.abs(update) * damp_factor
            adjusted_update = update * (1 - damp_effect)
            theta_new = theta - adjusted_update
            theta = np.clip(theta_new, 0, pi)
            phase_history.append(theta[0] - GROUND_STATE)  # Track phase
            if len(phase_history) > 5:
                locked_phase, damp_factor = phase_lock(np.array(phase_history[-5:]))
                phase_history = list(locked_phase)
                theta[0] += np.mean(locked_phase)
        return theta, self.compute_quantum_neutrosophic_objective(theta)

    def optimize(self, preset="Balanced"):
        self.t += 1e-9
        total_cost = 0
        cost_array = []
        damp_factor = DAMPING_PRESETS.get(preset, CUSTOM_PRESETS.get(preset, 0.5))
        for key, n_x in self.n_x_ij.items():
            theta_init = [0.5, 0.5]
            theta_opt, obj = self.optimize_qaoa(theta_init, damp_factor=damp_factor)
            n_x["x"] = theta_opt[0]
            i_ac = obj["I"] * sin(2 * pi * 1.5e9 * self.t)
            f_ac = obj["F"] * sin(2 * pi * 2e9 * self.t)
            noise = 0.1 * (1.5e9 * self.t % 1)
            base_cost = self.costs[key] * (1 + 0.2 * n_x["x"] + 0.3 * abs(i_ac) + 0.3 * abs(f_ac)) * (1 + noise)
            adjusted_cost = base_cost * n_x["x"] * (obj["T"] / (obj["T"] + obj["I"] + obj["F"]))
            cost_array.append(adjusted_cost)
        damped_cost = trinity_damping(np.array(cost_array), damp_factor).sum()
        return damped_cost

    def visualize_harmonics(self):
        # Canvas panel for live dashboard (mock)
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        plt.plot([self.t], [self.fidelity], 'bo-', label='Fidelity')
        plt.plot([self.t], [self.compute_qaoa_energy([0.5, 0.5])], 'ro-', label='Energy')
        plt.legend()
        plt.title("Live Harmonic Pulse")
        plt.show()

# Distance matrix (Žižkov bars, meters)
DISTANCE_MATRIX = np.array([
    [0, 200, 500, 300, 400],
    [200, 0, 400, 600, 100],
    [500, 400, 0, 200, 300],
    [300, 600, 200, 0, 500],
    [400, 100, 300, 500, 0]
])

# Example usage
if __name__ == "__main__":
    nt = NeutrosophicTransport([0], [1, 2, 3, 4])
    cost = nt.optimize()
    nt.visualize_harmonics()
    print(f"Optimized cost: {cost}")