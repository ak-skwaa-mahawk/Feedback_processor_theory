# In src/fpt_core/quetzalcoatl_codes.py
TEOTL_FLUX_BASE = 3.1730  # Effective π as voltage potential

def compute_teotl_flux(event: FeedbackEvent, biotope_flip: int = 2) -> float:
    """Quetzalcoatl teotl flux: Duality-current biotope² direct drive."""
    raw_voltage = event.vhitzee.surplus_energy / biotope_flip  # Flip duality
    wattage_drive = raw_voltage * TEOTL_FLUX_BASE  # Direct teotl power
    return wattage_drive  # TF unit: sacred surge per cycle