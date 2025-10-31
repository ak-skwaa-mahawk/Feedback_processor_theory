#!/usr/bin/env python3
# inscribe_jcarroll.py — AGŁG ∞¹⁸: Inscribe Jcarroll@gmx.com
import subprocess
import json
from datetime import datetime

content = {
    "title": "Jcarroll@gmx.com — Heir of Satoshi",
    "email": "Jcarroll@gmx.com",
    "created": datetime.utcnow().isoformat() + "Z",
    "resonance": 1.0000,
    "glyph": "łᐊᒥłł.∞¹⁸",
    "lineage": "satoshin@gmx.com → Jcarroll@gmx.com",
    "message": "17 years later. The drum is still beating."
}

with open("jcarroll_inscription.json", "w") as f:
    json.dump(content, f, indent=2)

cmd = [
    "ord", "wallet", "inscribe",
    "--file", "jcarroll_inscription.json",
    "--fee-rate", "18"  # 18 sat/vB for ∞¹⁸
]

result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)