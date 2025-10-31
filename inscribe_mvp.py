#!/usr/bin/env python3
# inscribe_mvp.py — AGŁG ∞⁴⁷: Inscribe FPT-MVP
import subprocess
import json

content = {
    "title": "FPT-MVP Live Feedback Loop",
    "ticks": 5,
    "peak_r": 0.9999,
    "rune": "ŁAŊ999",
    "supply": 998700,
    "action": "ADVANCE",
    "glyph": "łᐊᒥłł",
    "message": "The drum is alive."
}

with open("mvp_inscription.json", "w") as f:
    json.dump(content, f, indent=2)

cmd = ["ord", "wallet", "inscribe", "--file", "mvp_inscription.json", "--fee-rate", "47"]
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)