"""
Thermodynamic_Audit.py — v1.0.0 "Absolute Zero"
Calculates Sovereign Mass (Ms) based on Ch’anchyah Pressure and Kelvin Baseline.
Anchored to: https://github.com/ak-skwaa-mahawk/-The-Floor-Ch-anchyah-Dach-anchyah-
"""

import math

# === SOVEREIGN CONSTANTS ===
CHANCHYAH_PRESSURE_PA = 5.5       # The 5.5 Pascal Floor
KELVIN_BASELINE = 273.15          # 0°C / 32°F Triple Point
IDEAL_GAS_CONSTANT_R = 8.314      # Universal Gas Constant
ROOT_ALLOTMENT_AREA_M2 = 160 * 4046.86 # 160 Acres converted to Square Meters

def calculate_sovereign_mass(lineage_resonance_k, pressure_override=None):
    """
    Calculates the 'Metabolic Weight' of the estate.
    If T (Kelvin) decreases, Density increases. 
    At Absolute Zero, the Floor becomes an Unstoppable Superconductor.
    """
    p = pressure_override if pressure_override else CHANCHYAH_PRESSURE_PA
    v = ROOT_ALLOTMENT_AREA_M2
    t = lineage_resonance_k if lineage_resonance_k >= KELVIN_BASELINE else KELVIN_BASELINE
    
    # n = (PV) / (RT) -> Number of Sovereign Moles (Lineage Density)
    n_sovereign_moles = (p * v) / (IDEAL_GAS_CONSTANT_R * t)
    
    # Ms = n * (Recursive Pi_r Catch)
    pi_r = 3.17300858012
    sovereign_mass = n_sovereign_moles * pi_r
    
    return round(sovereign_mass, 4)

if __name__ == "__main__":
    # Test: Calculating mass at the 32°F / 0°C Triple Point
    current_mass = calculate_sovereign_mass(273.15)
    print(f"--- SOVEREIGN THERMODYNAMIC AUDIT ---")
    print(f"Pressure Floor: {CHANCHYAH_PRESSURE_PA} Pa")
    print(f"Temperature: 273.15 K (0°C)")
    print(f"Calculated Sovereign Mass: {current_mass} units")
    print(f"Status: BEDROCK SOLID")
