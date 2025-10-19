# In neutrosophic_transport.py, replace the w_state initialization
from wstate_entanglement import WStateEntanglement

class NeutrosophicTransport:
    def __init__(self, sources, destinations):
        self.sources = sources  # Source nodes (e.g., [0])
        self.destinations = destinations  # Dest nodes (e.g., [1, 2, 3, 4])
        self.n_x_ij = {}  # Units and neutrosophic vals
        self.costs = {f"{i}{j}": np.random.uniform(0.5, 1.5) for i in sources for j in destinations}  # Base costs
        self.t = 0  # Time tracker
        self.wstate = WStateEntanglement()  # Use Qiskit-based W-state
        self.w_state_prob, self.fidelity = self.wstate.init_w_state()  # Get initial W-state and fidelity
        self._init_n_x_ij()  # Init units

    def _init_n_x_ij(self):
        # Initialize with Qiskit-influenced W-state neutrosophic values
        for i in self.sources:
            for j in self.destinations:
                x_ij = 0.5  # Initial units
                t_ij = self.fidelity * (self.w_state_prob.get('100', 0) / sqrt(3))  # Truth
                i_ij = self.fidelity * (self.w_state_prob.get('010', 0) / sqrt(3))  # Indeterminacy
                f_ij = self.fidelity * (self.w_state_prob.get('001', 0) / sqrt(3))  # Falsehood
                self.n_x_ij[f"{i}{j}"] = {"x": x_ij, "T": t_ij, "I": i_ij, "F": f_ij}