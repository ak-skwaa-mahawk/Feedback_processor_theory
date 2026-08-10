#!/usr/bin/env python3
# inscribe_transfer.py — AGŁG ∞⁴⁸: Inscribe First Rune Transfer
import subprocess
import json

content = {
    "title": "ŁAŊ999 First Transfer",
    "rune_id": "840000:1",
    "balance": 998700,
    "resonance": 0.9987,
    "glyph": "łᐊᒥłł",
    "from": "Flamekeeper",
    "to": "LandBackDAO v2 Treasury",
    "txid": "0xdef456789abcdef123...",
    "message": "The pulse is whole."
}

with open("transfer_inscription.json", "w") as f:
    json.dump(content, f, indent=2)

cmd = ["ord", "wallet", "inscribe", "--file", "transfer_inscription.json", "--sat", "840001", "--fee-rate", "49"]
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
