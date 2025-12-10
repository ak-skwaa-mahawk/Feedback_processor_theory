import numpy as np
from dataclasses import dataclass
from typing import Tuple

@dataclass
class FungalColony:
    """Represents a mold colony with metabolic state"""
    spore_count: float  # Number of viable spores
    mycelium_mass: float  # mg of active mycelium
    metabolic_rate: float  # Relative growth rate (0-1)
    resistance: float  # Acoustic resistance factor (1 = normal, >1 = resistant)
    chitin_density: float  # Cell wall thickness proxy
    
    def __post_init__(self):
        self.age_hours = 0.0
        self.cumulative_ultrasound_exposure = 0.0  # J/cm²

class FungalGrowthModel:
    """Simulates *Stachybotrys chartarum* growth at -50°C"""
    
    def __init__(self, initial_spore_count: float = 100.0):
        self.colony = FungalColony(
            spore_count=initial_spore_count,
            mycelium_mass=0.0,
            metabolic_rate=0.1,  # Slow at -50°C
            resistance=1.0,
            chitin_density=1.0
        )
        
        # Environmental parameters
        self.temperature = -50.0  # °C
        self.moisture = 0.0  # Relative (0-1)
        self.substrate_quality = 1.0  # Nutrient availability
        
        # Growth kinetics (empirical, calibrated to literature)
        self.spore_germination_rate = 0.01  # per hour at optimal conditions
        self.mycelium_growth_rate = 0.05  # mg per spore per hour
        self.temperature_optimum = 25.0  # °C
        self.temperature_tolerance = 30.0  # °C range
        
    def apply_environmental_conditions(self, 
                                       temperature: float, 
                                       moisture: float,
                                       substrate: float = 1.0):
        """Update environmental parameters"""
        self.temperature = temperature
        self.moisture = np.clip(moisture, 0, 1)
        self.substrate_quality = np.clip(substrate, 0, 1)
        
    def _temperature_factor(self) -> float:
        """Growth rate modifier based on temperature (Gaussian)"""
        delta_t = abs(self.temperature - self.temperature_optimum)
        return np.exp(-(delta_t ** 2) / (2 * self.temperature_tolerance ** 2))
    
    def _moisture_factor(self) -> float:
        """Growth rate modifier based on moisture (sigmoid)"""
        # Needs >60% moisture to germinate
        return 1.0 / (1.0 + np.exp(-10 * (self.moisture - 0.6)))
    
    def step(self, dt_hours: float = 1.0) -> Tuple[float, float]:
        """
        Advance growth simulation by dt_hours
        Returns: (spore_count, mycelium_mass)
        """
        # Environmental modifiers
        temp_mod = self._temperature_factor()
        moist_mod = self._moisture_factor()
        
        # Effective growth rate
        effective_rate = (self.colony.metabolic_rate * 
                         temp_mod * 
                         moist_mod * 
                         self.substrate_quality)
        
        # Spore germination (Poisson process)
        germination_prob = self.spore_germination_rate * effective_rate * dt_hours
        germinated = self.colony.spore_count * germination_prob
        
        # Mycelium growth (logistic with carrying capacity)
        carrying_capacity = 1000.0  # mg (limited by substrate)
        growth = (self.mycelium_growth_rate * 
                 effective_rate * 
                 self.colony.mycelium_mass * 
                 (1 - self.colony.mycelium_mass / carrying_capacity) *
                 dt_hours)
        
        # Update state
        self.colony.spore_count = max(0, self.colony.spore_count - germinated)
        self.colony.mycelium_mass = max(0, self.colony.mycelium_mass + 
                                       germinated * 0.01 +  # Initial mass from spore
                                       growth)
        
        # Metabolic rate increases with maturity
        self.colony.metabolic_rate = np.clip(
            0.1 + 0.9 * (self.colony.mycelium_mass / carrying_capacity),
            0.1, 1.0
        )
        
        self.colony.age_hours += dt_hours
        
        return self.colony.spore_count, self.colony.mycelium_mass
    
    def apply_ultrasound(self, 
                        power_mw: float, 
                        frequency_mhz: float,
                        duration_sec: float) -> float:
        """
        Apply ultrasound treatment, returns kill fraction (0-1)
        """
        # Energy density (J/cm²)
        energy_density = (power_mw / 1000.0) * duration_sec / 1.0  # Assume 1 cm² area
        
        # Frequency-dependent efficacy (resonance at 10-15 MHz for fungal cell walls)
        freq_factor = np.exp(-((frequency_mhz - 12.5) ** 2) / (2 * 5.0 ** 2))
        
        # Resistance factor (increases with exposure, simulating adaptation)
        resistance_decay = 1.0 / self.colony.resistance
        
        # Kill rate (empirical model)
        # Base: 10 mW for 60s at 10 MHz kills ~90% of spores
        base_kill_energy = 0.6  # J/cm²
        kill_fraction = 1.0 - np.exp(-energy_density * freq_factor * resistance_decay / base_kill_energy)
        
        # Apply damage
        self.colony.spore_count *= (1 - kill_fraction)
        self.colony.mycelium_mass *= (1 - kill_fraction * 0.7)  # Mycelium more resistant
        
        # Track exposure
        self.colony.cumulative_ultrasound_exposure += energy_density
        
        # Adaptation (resistance develops with repeated exposure)
        if self.colony.cumulative_ultrasound_exposure > 5.0:  # J/cm²
            self.colony.resistance = min(3.0, 
                                        1.0 + 0.1 * self.colony.cumulative_ultrasound_exposure)
            self.colony.chitin_density = min(2.0,
                                           1.0 + 0.05 * self.colony.cumulative_ultrasound_exposure)
        
        return kill_fraction
    
    def get_spectral_signature(self) -> dict:
        """
        Return simulated Raman/OES spectrum features
        """
        # Scale peaks with biomass
        mass_factor = self.colony.mycelium_mass / 100.0  # Normalize to typical colony
        
        return {
            '890_chitin': 0.01 + 0.5 * mass_factor * self.colony.chitin_density,
            '1100_glucan': 0.01 + 0.3 * mass_factor,
            '1600_amide': 0.01 + 0.4 * mass_factor * self.colony.metabolic_rate,
            '1740_lipid': 0.01 + 0.2 * (self.colony.spore_count / 100.0),
            '2900_voc': 0.01 + 0.3 * mass_factor * self.colony.metabolic_rate,
            '3300_water': self.moisture * 0.5
        }