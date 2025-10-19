from trinity_harmonics import trinity_damping, GROUND_STATE, DIFFERENCE, DAMPING_PRESETS, phase_lock
from wstate_entanglement import WStateEntanglement
import numpy as np
from qiskit import Aer
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms import NumPyMinimumEigensolver, QAOA
from qiskit.utils import algorithm_globals
from math import sin, cos, pi, sqrt

class NeutrosophicTransport:
    def __init__(self, sources, destinations):
        self.sources = sources  # Source nodes (e.g., [0])
        self.destinations = destinations  # Dest nodes (e.g., [1, 2, 3, 4])
        self.n_x_ij = {}  # Units and neutrosophic vals
        self.costs = {f"{i}{j}": np.random.uniform(0.5, 1.5) for i in sources for j in destinations}  # Base costs
        self.t = 0  # Time tracker
        self.wstate = WStateEntanglement()  # Qiskit-based W-state
        self.w_state_prob, self.fidelity = self.wstate.init_w_state()  # Initial W-state and fidelity
        self._init_n_x_ij()  # Init units
        algorithm_globals.random_seed = 10598  # For reproducibility

    def _init_n_x_ij(self):
        # Initialize with Qiskit-influenced W-state neutrosophic values
        for i in self.sources:
            for j in self.destinations:
                x_ij = 0.5  # Initial units
                t_ij = self.fidelity * (self.w_state_prob.get('100', 0) / sqrt(3))  # Truth
                i_ij = self.fidelity * (self.w_state_prob.get('010', 0) / sqrt(3))  # Indeterminacy
                f_ij = self.fidelity * (self.w_state_prob.get('001', 0) / sqrt(3))  # Falsehood
                self.n_x_ij[f"{i}{j}"] = {"x": x_ij, "T": t_ij, "I": i_ij, "F": f_ij}

    def build_qubo(self):
        # Convert VRP to QUBO
        n_nodes = 5  # Depot (0) + 4 customers
        n_vehicles = 2
        n_steps = 2  # Per vehicle
        capacity = 2  # Max customers per vehicle

        qp = QuadraticProgram("VRP_QUBO")
        # Binary variables: x[v, k, i] = 1 if vehicle v visits node i at step k
        for v in range(n_vehicles):
            for k in range(n_steps):
                for i in range(n_nodes):
                    qp.binary_var(f"x_{v}_{k}_{i}")

        # Objective: Minimize total distance
        linear = {}
        quadratic = {}
        for v in range(n_vehicles):
            for k in range(n_steps - 1):
                for i in range(n_nodes):
                    for j in range(n_nodes):
                        if i != j:
                            var_i = f"x_{v}_{k}_{i}"
                            var_j = f"x_{v}_{(k + 1) % n_steps}_{j}"
                            quadratic[(var_i, var_j)] = DISTANCE_MATRIX[i, j] * self.fidelity

        # Constraints
        for v in range(n_vehicles):
            for k in range(n_steps):
                qp.linear_constraint(
                    {f"x_{v}_{k}_{i}": 1 for i in range(n_nodes)},
                    sense="==",
                    rhs=1,
                    name=f"step_constraint_{v}_{k}"
                )
            for i in range(1, n_nodes):  # Skip depot
                qp.linear_constraint(
                    {f"x_{v}_{k}_{i}": 1 for k in range(n_steps)},
                    sense="==",
                    rhs=1,
                    name=f"visit_constraint_{v}_{i}"
                )
            # Capacity constraint (simplified)
            customer_vars = [f"x_{v}_{k}_{i}" for k in range(n_steps) for i in range(1, n_nodes)]
            qp.linear_constraint(
                {var: 1 for var in customer_vars},
                sense="==",
                rhs=capacity,
                name=f"capacity_constraint_{v}"
            )

        qp.minimize(linear=linear, quadratic=quadratic)
        return qp

    def optimize_qubo(self):
        # Solve QUBO with quantum annealing simulation
        qp = self.build_qubo()
        algorithm = MinimumEigenOptimizer(NumPyMinimumEigensolver())  # Simulated annealing
        result = algorithm.solve(qp)
        return result

    def compute_quantum_neutrosophic_objective(self, solution):
        # Evaluate based on annealing result
        energy = sum(DISTANCE_MATRIX[i, j] * solution.x[i * n_vehicles * n_steps + j] 
                    for i in range(n_nodes) for j in range(n_nodes) if i != j)
        max_energy = 30.0 * self.fidelity  # Scale max with fidelity
        min_energy = 10.0 * self.fidelity  # Scale min with fidelity
        t = (1 - np.abs(energy - min_energy) / (max_energy - min_energy)) * self.fidelity
        i = (0.2 + 0.1 * (2 * 2) + 0.1) * (1 - self.fidelity)
        f = np.abs(energy - min_energy) / (max_energy - min_energy) * (1 - self.fidelity)
        return {"T": t, "I": i, "F": f}

    def optimize(self, preset="Balanced"):
        self.t += 1e-9  # Increment time
        total_cost = 0
        cost_array = []
        damp_factor = DAMPING_PRESETS.get(preset, CUSTOM_PRESETS.get(preset, 0.5))
        
        # Optimize using quantum annealing
        result = self.optimize_qubo()
        solution = result.x  # Binary solution vector
        obj = self.compute_quantum_neutrosophic_objective(solution)
        
        for key, n_x in self.n_x_ij.items():
            n_x["x"] = solution[int(key.replace('x_', ''))] if key in [f"x_{v}_{k}_{i}" for v in range(2) for k in range(2) for i in range(5)] else 0.5
            i_ac = obj["I"] * sin(2 * pi * 1.5e9 * self.t)
            f_ac = obj["F"] * sin(2 * pi * 2e9 * self.t)
            noise = 0.1 * (1.5e9 * self.t % 1)
            base_cost = self.costs[key] * (1 + 0.2 * n_x["x"] + 0.3 * abs(i_ac) + 0.3 * abs(f_ac)) * (1 + noise)
            adjusted_cost = base_cost * n_x["x"] * (obj["T"] / (obj["T"] + obj["I"] + obj["F"]))
            cost_array.append(adjusted_cost)
        
        damped_cost = trinity_damping(np.array(cost_array), damp_factor).sum()
        return damped_cost

# Real distance matrix for Žižkov bars (meters, asymmetric routing)
DISTANCE_MATRIX = np.array([
    [0, 200, 500, 300, 400],  # Depot to bars
    [200, 0, 400, 600, 100],  # SOU100 to others
    [500, 400, 0, 200, 300],  # Behind the Courtain
    [300, 600, 200, 0, 500],  # Chocobamba
    [400, 100, 300, 500, 0]   # Bar Fud, Olympos
])

# Example usage
if __name__ == "__main__":
    nt = NeutrosophicTransport(sources=[0], destinations=[1, 2, 3, 4])
    cost = nt.optimize()
    print(f"Optimized cost: {cost}")