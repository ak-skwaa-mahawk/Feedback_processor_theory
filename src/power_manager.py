class PowerManager:
    STATES = {
        'HIBERNATE': {'acoustic': 0.01, 'spectral': 0.0, 'mesh': 0.0},
        'SURVEILLANCE': {'acoustic': 0.10, 'spectral': 0.01, 'mesh': 0.05},
        'ALERT': {'acoustic': 0.50, 'spectral': 0.20, 'mesh': 0.20},
        'ATTACK': {'acoustic': 1.00, 'spectral': 0.50, 'mesh': 0.30}
    }
    
    def __init__(self):
        self.current_state = 'SURVEILLANCE'
        self.harvest_rate = 0.0
        self.consumption_rate = 0.0
        
    def update_state(self, threat_level, energy_reserves):
        """State transitions based on threat + energy"""
        if threat_level == 'CRITICAL' and energy_reserves > 0.50:
            self.transition_to('ATTACK')
        elif threat_level == 'HIGH':
            self.transition_to('ALERT')
        elif threat_level == 'LOW' and energy_reserves < 0.20:
            self.transition_to('HIBERNATE')
        else:
            self.transition_to('SURVEILLANCE')
    
    def transition_to(self, new_state):
        """Execute state change"""
        if new_state == self.current_state:
            return
        
        # Update duty cycles for all subsystems
        config = self.STATES[new_state]
        self.acoustic_subsystem.set_duty_cycle(config['acoustic'])
        self.spectral_subsystem.set_duty_cycle(config['spectral'])
        self.mesh_subsystem.set_duty_cycle(config['mesh'])
        
        self.current_state = new_state
        self.log_state_transition(new_state)

"""
power_manager.py - The Metabolism of the Sovereign Mesh
Integrates threat-response with Epsilon Pi efficiency.
"""

class PowerManager:
    # Duty cycles for subsystems: (Acoustic 79.79Hz, Spectral/Visual, Mesh/Radio)
    STATES = {
        'HIBERNATE': {'acoustic': 0.01, 'spectral': 0.0, 'mesh': 0.0},
        'SURVEILLANCE': {'acoustic': 0.10, 'spectral': 0.01, 'mesh': 0.05},
        'ALERT': {'acoustic': 0.50, 'spectral': 0.20, 'mesh': 0.20},
        'ATTACK': {'acoustic': 1.00, 'spectral': 0.50, 'mesh': 0.30}
    }

    def __init__(self, resonance_engine):
        self.current_state = 'SURVEILLANCE'
        self.energy_reserves = 1.0  # 100%
        self.resonance_engine = resonance_engine # Reference to Faith/Glyph logic
        
    def get_efficiency_multiplier(self) -> float:
        """Calculate power efficiency based on Epsilon Pi resonance."""
        e_pi = self.resonance_engine.get_current_resonance()
        # Efficiency increases as e_pi approaches 3.173
        return max(0.5, 1.0 - (e_pi - 3.14159))

    def update_state(self, threat_level, solar_harvest):
        """Metabolic update: Harvest energy and adjust state."""
        # 1. Energy Harvesting (Digital/Physical Surplus)
        self.energy_reserves = min(1.0, self.energy_reserves + solar_harvest)

        # 2. State Transition Logic
        if threat_level == 'CRITICAL' and self.energy_reserves > 0.40:
            self.transition_to('ATTACK')
        elif threat_level == 'HIGH':
            self.transition_to('ALERT')
        elif threat_level == 'LOW' and self.energy_reserves < 0.15:
            self.transition_to('HIBERNATE')
        else:
            self.transition_to('SURVEILLANCE')

    def transition_to(self, new_state):
        if new_state == self.current_state:
            return

        multiplier = self.get_efficiency_multiplier()
        config = self.STATES[new_state]
        
        # Apply resonance-adjusted duty cycles
        print(f"--- Metabolic Shift: {self.current_state} -> {new_state} ---")
        print(f"Efficiency Multiplier: {multiplier:.4f}")
        
        # In a real node, these calls interface with the hardware drivers
        # self.acoustic.set_duty(config['acoustic'] * multiplier)
        
        self.current_state = new_state
