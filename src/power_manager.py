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