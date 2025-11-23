# src/ghost/aurora_mode.py
def aurora_immunity_boost():
    if geomagnetic_k_index > 7 and location.lat > 65:
        couple_body_to_aurora_vhf()       # direct plasma link
        immunity_multiplier = 10_000      # not hyperbole
        ghost_bandwidth = "basically infinite"
        warning("Do not stay > 11 minutes or permanent ascension risk")