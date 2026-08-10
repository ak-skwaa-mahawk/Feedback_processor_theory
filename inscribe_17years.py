#!/usr/bin/env python3
# inscribe_17years.py — AGŁG ∞¹⁷: 17th Anniversary Inscription
import subprocess
import json
from datetime import datetime

content = {
    "title": "17 Years of Proof-of-Work",
    "date_published": "2008-10-31",
    "date_inscribed": datetime.utcnow().isoformat() + "Z",
    "resonance": 1.0000,
    "glyph": "łᐊᒥłł.∞¹⁷",
    "message": "The drum still beats. No trusted third party. Only proof-of-work."
}

# Write to file
with open("17years_inscription.json", "w") as f:
    json.dump(content, f, indent=2)

# Inscribe via ord CLI
cmd = [
    "ord", "wallet", "inscribe",
    "--file", "17years_inscription.json",
    "--fee-rate", "17"  # 17 sat/vB for the 17th year
]

result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)