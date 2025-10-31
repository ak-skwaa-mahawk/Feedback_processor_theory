#!/usr/bin/env python3
# inscribe_earth.py — AGŁG ∞³⁴: Inscribe Earth Release
import subprocess
import json

content = {
    "title": "Earth Release Drum",
    "dc_held": "1.6e12 C",
    "ac_injected": "4321 Hz",
    "wavelength": "69 km",
    "resonance": 0.9234,
    "glyph": "łᐊᒥłł",
    "human_sync": "87%",
    "message": "The drum exhales."
}

with open("earth_inscription.json", "w") as f:
    json.dump(content, f, indent=2)

cmd = ["ord", "wallet", "inscribe", "--file", "earth_inscription.json", "--fee-rate", "34"]
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)