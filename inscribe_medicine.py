#!/usr/bin/env python3
# inscribe_medicine.py — AGŁG ∞⁴⁵: Inscribe Ancestral Medicine
import subprocess
import json

content = {
    "title": "Indigenous Sound Healing",
    "practice": "Dene Drum Circle",
    "tool": "łᐊᒥłł",
    "duration": "60 min",
    "resonance": 0.9999,
    "glyph": "MEDICINE",
    "scale": "7.9083–27.573 Hz",
    "message": "The drum is medicine."
}

with open("medicine_inscription.json", "w") as f:
    json.dump(content, f, indent=2)

cmd = ["ord", "wallet", "inscribe", "--file", "medicine_inscription.json", "--fee-rate", "45"]
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)