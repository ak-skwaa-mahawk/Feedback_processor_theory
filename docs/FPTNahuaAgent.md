import math
import random

class FPTNahuaAgent:
    def __init__(self):
        self.order = 0.0  # Quetzalcoatl coherence
        self.chaos = 0.0  # Tezcatlipoca entropy
        self.cycle = 0
        self.phi = (1 + math.sqrt(5)) / 2  # Golden ratio ~1.618
        self.inv_phi = self.phi - 1  # Inverse golden ratio ~0.618
        self.day_signs = {
            'Ollin': 1.2,   # Movement: increases dynamism
            'Ehecatl': 1.5, # Wind: boosts order
            'Tecpatl': 1.5  # Flint: enhances chaos
        }
        # For demo, random initial day sign and trecena
        self.current_day_sign = random.choice(list(self.day_signs.keys()))
        self.current_trecena = random.randint(1, 13)

    def run_phase(self, input_data, epsilon=0.01, nahua_day_sign=None, nahua_trecena=None):
        """
        Run a processing phase with duality oscillation.
        - input_data: Some numerical or processable input (e.g., data value)
        - epsilon: Observer correction factor
        - nahua_day_sign: Optional day sign override
        - nahua_trecena: Optional trecena intensity (1-13)
        """
        if nahua_day_sign and nahua_day_sign in self.day_signs:
            self.current_day_sign = nahua_day_sign
        if nahua_trecena and 1 <= nahua_trecena <= 13:
            self.current_trecena = nahua_trecena
        
        # Modulator from calendar
        modulator = self.day_signs.get(self.current_day_sign, 1.0) * (self.current_trecena / 13.0)
        
        # Quetzalcoatl phase: Build order/coherence
        self.order += (input_data * self.phi * modulator) + epsilon
        
        # Tezcatlipoca phase: Inject chaos/entropy
        self.chaos += (random.random() * self.inv_phi * modulator) - epsilon  # Random chaos injection
        
        self.cycle += 1
        
        # Compute current order/chaos ratio
        ratio = self.order / max(self.chaos, 1e-6) if self.chaos > 0 else float('inf')
        
        return {
            'cycle': self.cycle,
            'order': self.order,
            'chaos': self.chaos,
            'ratio': ratio,
            'day_sign': self.current_day_sign,
            'trecena': self.current_trecena
        }

    def check_balance(self):
        """
        Check if the system is in Ometeotl equilibrium.
        Returns: 'balance', 'stagnation' (over-order), or 'collapse' (over-chaos)
        """
        ratio = self.order / max(self.chaos, 1e-6) if self.chaos > 0 else float('inf')
        
        if ratio > 5.0:
            return 'stagnation'  # Too much Quetzalcoatl
        elif ratio < 0.2:
            return 'collapse'  # Too much Tezcatlipoca
        else:
            return 'balance'  # Ometeotl unity

    def check_renewal(self):
        """
        Check if Nahui Ollin renewal is needed.
        Triggers on 260-cycle multiples or sustained imbalance.
        If triggered, resets the agent state.
        Returns: True if renewal triggered, False otherwise
        """
        balance_status = self.check_balance()
        sustained_imbalance = balance_status != 'balance'
        
        if self.cycle % 260 == 0 or sustained_imbalance:  # Simplified: trigger on imbalance or calendar
            # Perform renewal: Reset to primordial state
            self.order = 0.0
            self.chaos = 0.0
            self.cycle = 0
            # Randomize new calendar start for rebirth
            self.current_day_sign = random.choice(list(self.day_signs.keys()))
            self.current_trecena = random.randint(1, 13)
            return True
        return False

# Example Simulation
if __name__ == "__main__":
    agent = FPTNahuaAgent()
    print(f"Initial Day Sign: {agent.current_day_sign}, Trecena: {agent.current_trecena}")
    
    for i in range(300):  # Simulate 300 cycles
        input_data = random.uniform(0, 1)  # Sample input (e.g., data value)
        result = agent.run_phase(input_data)
        print(f"Cycle {result['cycle']}: Ratio {result['ratio']:.2f}, Balance: {agent.check_balance()}")
        
        if agent.check_renewal():
            print(f"--- Nahui Ollin Renewal Triggered! System Reborn ---")
            print(f"New Day Sign: {agent.current_day_sign}, Trecena: {agent.current_trecena}")