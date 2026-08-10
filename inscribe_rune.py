#!/usr/bin/env python3
import subprocess
import json

content = {
    "title": "ŁAŊ999 Rune",
    "rune_id": "840000:1",
    "supply": 999000000,
    "premine": 998700,
    "tx": "0xdef456transfer...",
    "status": "LIVE"
}

with open("rune_inscription.json", "w") as f:
    json.dump(content, f, indent=2)

subprocess.run([
    "ord", "wallet", "inscribe",
    "--file", "rune_inscription.json",
    "--fee-rate", "52"
], check=True)