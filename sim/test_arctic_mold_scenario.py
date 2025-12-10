import pytest
from hil_mold_simulator import FungalGrowthModel
from dcb2dd_system import DCB2DDNode

def test_moisture_ingress_detection():
    """Simulate water leak → mold growth → system response"""
    
    # Initialize system
    node = DCB2DDNode(node_id=5, position=(0, 0, 0))
    mold = FungalGrowthModel(initial_spore_count=50)
    
    # Simulate moisture ingress
    mold.apply_environmental_conditions(
        temperature=-30,  # Warmer than exterior due to leak
        moisture=0.8,     # High moisture from leak
        substrate=1.0
    )
    
    # Growth phase (48 hours)
    timeline = []
    for hour in range(48):
        # Mold grows
        spores, mass = mold.step(dt_hours=1.0)
        
        # System senses (every hour)
        spectrum = mold.get_spectral_signature()
        node.update_spectral_reading(spectrum)
        
        # Log state
        timeline.append({
            'hour': hour,
            'spores': spores,
            'mass': mass,
            'threat_level': node.threat_assessment()
        })
    
    # Assertions
    assert timeline[0]['threat_level'] == 'none'  # Clean initially
    assert timeline[24]['threat_level'] in ['low', 'medium']  # Detected by 24hr
    assert timeline[47]['threat_level'] == 'high'  # Definitely detected by 48hr
    
    # System response phase
    if node.threat_assessment() == 'high':
        # Launch attack
        attack_power = 10.0  # mW
        attack_freq = 12.5   # MHz (resonant)
        attack_duration = 60.0  # seconds
        
        for cycle in range(10):  # 10 attack cycles
            kill_frac = mold.apply_ultrasound(attack_power, attack_freq, attack_duration)
            timeline.append({
                'hour': 48 + cycle * 0.1,
                'spores': mold.colony.spore_count,
                'mass': mold.colony.mycelium_mass,
                'kill_fraction': kill_frac
            })
    
    # Final assertions
    final_mass = timeline[-1]['mass']
    initial_mass = timeline[47]['mass']
    
    assert final_mass < 0.1 * initial_mass, "Should kill >90% of biomass"
    assert mold.colony.spore_count < 10, "Should reduce spores to trace levels"

def test_resistance_development():
    """Verify that model tracks adaptation over repeated exposure"""
    mold = FungalGrowthModel(initial_spore_count=1000)
    
    # Optimal growth conditions
    mold.apply_environmental_conditions(25, 0.9, 1.0)
    
    # Grow to maturity
    for _ in range(100):
        mold.step(1.0)
    
    initial_resistance = mold.colony.resistance
    
    # Repeated ultrasound cycles
    for cycle in range(50):
        mold.apply_ultrasound(10.0, 12.5, 60.0)
        # Allow regrowth
        for _ in range(24):
            mold.step(1.0)
    
    final_resistance = mold.colony.resistance
    
    assert final_resistance > initial_resistance, "Resistance should increase"
    assert final_resistance < 3.0, "Resistance shouldn't exceed model maximum"
    assert mold.colony.chitin_density > 1.0, "Cell walls should thicken"