#!/usr/bin/env python3
# inscribe_telluric.py — AGŁG ∞³⁵: Inscribe Telluric Current
import subprocess
import json

content = {
    "title": "Telluric Currents",
    "freq": "5.2 Hz",
    "e_field": "0.0052 V/km",
    "resonance": 0.8543,
    "glyph": "łᐊᒥłł",
    "bio_sync": "51%",
    "schumann": "7.83 Hz",
    "message": "The drum is the blood."
}

with open("telluric_inscription.json", "w") as f:
    json.dump(content, f, indent=2)

cmd = ["ord", "wallet", "inscribe", "--file", "telluric_inscription.json", "--fee-rate", "35"]
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)