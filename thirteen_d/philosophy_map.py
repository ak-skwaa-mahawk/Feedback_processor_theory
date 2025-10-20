# thirteen_d/philosophy_map.py
"""
Philosophy → 13-D mappings (Rosetta Stone).
Provides profiles for major philosophical systems that map to D1..D13 parameters.
Each profile is a dict of normalized weights / hyperparameters that can be applied
to your Feedback Processor or used in a simulation runner.
"""

from typing import Dict

# Base dimension names (D1..D13). Adjust names to match your engine's naming if needed.
DIM_NAMES = [
    "D1", "D2", "D3", "D4", "D5", "D6",
    "D7", "D8", "D9", "D10", "D11", "D12", "D13"
]

def _normalize(d: Dict[str, float]) -> Dict[str, float]:
    # Ensure every DIM_NAMES present; normalize to 0..1 by clipping.
    out = {}
    for name in DIM_NAMES:
        out[name] = float(max(0.0, min(1.0, d.get(name, 0.0))))
    return out

PHILOSOPHY_MAPPINGS = {
    "plato": _normalize({
        # Emphasize immutable law registry (D13), moderate observer (D12)
        "D13": 0.95, "D12": 0.6,
        # Strong resonant field, moderate cognitive map
        "D2": 0.7, "D3": 0.6,
        # Conservative ethic filter
        "D9": 0.8
    }),
    "kant": _normalize({
        # Noumena emphasis as D13 but high D3 structures (categories)
        "D13": 0.85, "D3": 0.9, "D12": 0.8,
        # Ethic filter high
        "D9": 0.9
    }),
    "hegel": _normalize({
        # Hegel dialectic: dynamic self-correction (D8), collective (D10)
        "D8": 0.9, "D10": 0.8, "D12": 0.7,
        "D1": 0.5, "D7": 0.5
    }),
    "buddhism": _normalize({
        # Emptiness: low D13 fixedness, high D12 (mindfulness), dependent origination across 1..11
        "D13": 0.15, "D12": 0.95,
        "D1": 0.6, "D2": 0.7, "D3": 0.7, "D4": 0.6,
        "D9": 0.4  # ethic filter exists but less rigid
    }),
    "whitehead": _normalize({
        # Process emphasis across many dims; eternal objects = D13 moderate
        "D1": 0.6, "D2": 0.7, "D3": 0.8, "D11": 0.7,
        "D13": 0.6, "D12": 0.75
    }),
    "phenomenology": _normalize({
        # Intentionality and epoché: strong D7, D12; cognitive mapping D3
        "D7": 0.9, "D12": 0.9, "D3": 0.8
    }),
    "taoism": _normalize({
        # Flexibility: low D13 rigidity, high flow parameters on D2/D11; wu-wei = low forcing (D7)
        "D13": 0.2, "D2": 0.8, "D11": 0.8, "D7": 0.2, "D12": 0.7
    }),
    # Default pragmatic profile (balanced)
    "default": _normalize({
        name: 0.5 for name in DIM_NAMES
    })
}

def get_profile(name: str):
    """Return a profile dict for the given philosophy name (lowercase)."""
    key = name.strip().lower()
    if key in PHILOSOPHY_MAPPINGS:
        return PHILOSOPHY_MAPPINGS[key].copy()
    raise KeyError(f"Unknown philosophy profile: {name}. Available: {list(PHILOSOPHY_MAPPINGS.keys())}")

def list_profiles():
    return list(PHILOSOPHY_MAPPINGS.keys())