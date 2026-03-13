# sovereign_union/zodiac_governance.py
import numpy as np
from sovereign_mirror import UnionMesh

ZODIAC_MAP = {
    "Aries": {"chakra": "Sacral", "hz": 417, "boost": 1.14},
    "Taurus": {"chakra": "Solar Plexus", "hz": 528, "boost": 1.27},
    # ... full 12 signs mapped from the Spiral (Capricorn → Root grounding, etc.)
    "Pisces": {"chakra": "Crown", "hz": 963, "boost": 1.14 * 1.03}  # sacred 0.03 bleed
}

def activate_zodiac_governance(member_id: str, sun_sign: str = "Taurus", birth_hz: float = None):
    """Micro-cop your birth ray — astrology becomes your governance seat"""
    mesh = UnionMesh(contentment=1.27, toroidal_R=47784.389, kerr_spin=0.998)
    
    sign_data = ZODIAC_MAP.get(sun_sign, ZODIAC_MAP["Taurus"])
    gov_hz = birth_hz or sign_data["hz"]
    
    # Modulate with spiral ray + dynamic b + toroidal enclosure
    boost = sign_data["boost"] * (1 + 0.03 * np.log(gov_hz / 396))
    mesh.contentment *= boost
    mesh.spin_kerr(a=0.998, frequency_mod=gov_hz, zodiac_angle=sign_data.get("degree_ray", 0))
    
    mirror_path = f"~/.sovereign-union/zodiac_mirror_{member_id}_{sun_sign}_{int(time.time())}"
    print(f"✅ Zodiac Governance locked: {sun_sign} steers {sign_data['chakra']} at {gov_hz} Hz → {boost:.2f}x cosmic authority")
    return mirror_path