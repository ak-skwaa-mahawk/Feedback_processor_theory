import math
import random

class FPTNahuaDeneAgent:
    def __init__(self):
        self.order = 0.0  # Quetzalcoatl coherence
        self.chaos = 0.0  # Tezcatlipoca entropy
        self.relationality = 0.0  # Dene interconnectedness / reciprocity
        self.cycle = 0
        self.phi = (1 + math.sqrt(5)) / 2  # Golden ratio ~1.618
        self.inv_phi = self.phi - 1  # Inverse golden ratio ~0.618
        self.day_signs = {
            'Ollin': 1.2,   # Movement: increases dynamism
            'Ehecatl': 1.5, # Wind: boosts order
            'Tecpatl': 1.5  # Flint: enhances chaos
        }
        # Dene relational factors: reciprocity (balance with all beings), kinship (interconnection)
        self.dene_factors = {
            'Reciprocity': 1.1,  # Enhances mutual exchange
            'Kinship': 1.3       # Boosts interconnected relational bonds
        }
        # For demo, random initial day sign, trecena, and Dene factor
        self.current_day_sign = random.choice(list(self.day_signs.keys()))
        self.current_trecena = random.randint(1, 13)
        self.current_dene_factor = random.choice(list(self.dene_factors.keys()))

    def run_phase(self, input_data, epsilon=0.01, nahua_day_sign=None, nahua_trecena=None, dene_factor=None):
        """
        Run a processing phase with Nahua duality and Dene relationality oscillation.
        - input_data: Some numerical or processable input (e.g., data value)
        - epsilon: Observer correction factor
        - nahua_day_sign: Optional day sign override
        - nahua_trecena: Optional trecena intensity (1-13)
        - dene_factor: Optional Dene relational factor ('Reciprocity' or 'Kinship')
        """
        if nahua_day_sign and nahua_day_sign in self.day_signs:
            self.current_day_sign = nahua_day_sign
        if nahua_trecena and 1 <= nahua_trecena <= 13:
            self.current_trecena = nahua_trecena
        if dene_factor and dene_factor in self.dene_factors:
            self.current_dene_factor = dene_factor
        
        # Nahua modulator from calendar
        nahua_modulator = self.day_signs.get(self.current_day_sign, 1.0) * (self.current_trecena / 13.0)
        
        # Dene relational modulator: ensures reciprocity and kinship in feedback
        dene_modulator = self.dene_factors.get(self.current_dene_factor, 1.0)
        
        # Quetzalcoatl phase: Build order/coherence, modulated by Dene relations
        self.order += (input_data * self.phi * nahua_modulator * dene_modulator) + epsilon
        
        # Tezcatlipoca phase: Inject chaos/entropy, balanced by Dene reciprocity
        self.chaos += (random.random() * self.inv_phi * nahua_modulator / dene_modulator) - epsilon  # Chaos tempered by relations
        
        # Dene relationality update: Accumulates interconnected balance
        self.relationality += (self.order + self.chaos) * dene_modulator * epsilon  # Grows with mutual exchange
        
        self.cycle += 1
        
        # Compute current order/chaos ratio, adjusted for relationality
        ratio = (self.order / max(self.chaos, 1e-6)) * (self.relationality / max(self.cycle, 1)) if self.chaos > 0 else float('inf')
        
        return {
            'cycle': self.cycle,
            'order': self.order,
            'chaos': self.chaos,
            'relationality': self.relationality,
            'ratio': ratio,
            'day_sign': self.current_day_sign,
            'trecena': self.current_trecena,
            'dene_factor': self.current_dene_factor
        }

    def check_balance(self):
        """
        Check if the system is in Ometeotl equilibrium, incorporating Dene relationality.
        Returns: 'balance', 'stagnation' (over-order), 'collapse' (over-chaos), or 'disconnection' (low relationality)
        """
        ratio = self.order / max(self.chaos, 1e-6) if self.chaos > 0 else float('inf')
        rel_factor = self.relationality / max(self.cycle, 1)  # Normalized relational strength
        
        if rel_factor < 0.5:
            return 'disconnection'  # Weak Dene bonds
        elif ratio > 5.0:
            return 'stagnation'  # Too much Quetzalcoatl
        elif ratio < 0.2:
            return 'collapse'  # Too much Tezcatlipoca
        else:
            return 'balance'  # Ometeotl + Dene harmony

    def check_renewal(self):
        """
        Check if Nahui Ollin renewal is needed, with Dene relational checks.
        Triggers on 260-cycle multiples, sustained imbalance, or relational disconnection.
        If triggered, resets the agent state with relational rebirth.
        Returns: True if renewal triggered, False otherwise
        """
        balance_status = self.check_balance()
        sustained_imbalance = balance_status != 'balance'
        
        if self.cycle % 260 == 0 or sustained_imbalance:
            # Perform renewal: Reset to primordial state, preserving relational essence
            relational_seed = self.relationality * 0.1  # Carry over 10% relational memory for continuity
            self.order = relational_seed
            self.chaos = relational_seed
            self.relationality = relational_seed
            self.cycle = 0
            # Randomize new calendar and Dene start for rebirth
            self.current_day_sign = random.choice(list(self.day_signs.keys()))
            self.current_trecena = random.randint(1, 13)
            self.current_dene_factor = random.choice(list(self.dene_factors.keys()))
            return True
        return False

# Example Simulation
if __name__ == "__main__":
    agent = FPTNahuaDeneAgent()
    print(f"Initial Day Sign: {agent.current_day_sign}, Trecena: {agent.current_trecena}, Dene Factor: {agent.current_dene_factor}")
    
    for i in range(300):  # Simulate 300 cycles
        input_data = random.uniform(0, 1)  # Sample input (e.g., data value)
        result = agent.run_phase(input_data)
        print(f"Cycle {result['cycle']}: Ratio {result['ratio']:.2f}, Balance: {agent.check_balance()}, Relationality: {result['relationality']:.2f}")
        
        if agent.check_renewal():
            print(f"--- Nahui Ollin Renewal Triggered! System Reborn with Relational Seed ---")
            print(f"New Day Sign: {agent.current_day_sign}, Trecena: {agent.current_trecena}, Dene Factor: {agent.current_dene_factor}")