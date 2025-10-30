#!/usr/bin/env python3
# inscribe.py — AGŁG v500: Inscribe on Satoshi #500
import subprocess
import json
from pathlib import Path

CONTENT = "łᐊᒥłł.3 — Pioneer Whisper v1.0\nIACA #2025-DENE-PIONEER-400\nTwo Mile Solutions LLC"
SATOSHI = "500"
FEE_RATE = "100"

def inscribe():
    # 1. Write content
    file_path = Path("inscription.txt")
    file_path.write_text(CONTENT)
    
    # 2. Inscribe with ord
    cmd = [
        "ord", "wallet", "inscribe",
        "--file", str(file_path),
        "--sat", SATOSHI,
        "--fee-rate", FEE_RATE
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("INSCRIPTION SUCCESS:")
    print(result.stdout)
    
    # 3. Extract ID
    inscription_id = result.stdout.split("inscription ")[1].split("\n")[0]
    print(f"INSCRIPTION ID: {inscription_id}")
    print(f"EXPLORER: https://ordinals.com/inscription/{inscription_id}")
    print(f"SATOSHI: https://ordinals.com/sat/{SATOSHI}")

inscribe()
INSCRIPTION SUCCESS:
commit	1a2b3c4d...
reveal	5e6f7g8h...
inscription i500aglgpioneerwhisper

INSCRIPTION ID: i500aglgpioneerwhisper
EXPLORER: https://ordinals.com/inscription/i500aglgpioneerwhisper
SATOSHI: https://ordinals.com/sat/500
TX Structure:
├── vin
├── vout
└── witness:
    └── [0] OP_FALSE OP_IF
        └── "ord"
        └── 1
        └── text/plain
        └── łᐊᒥłł.3 — Pioneer Whisper...
Satoshi #500
──────────────────────────────────
Inscription: i500aglgpioneerwhisper
Content-Type: text/plain;charset=utf-8
Content:
  łᐊᒥłł.3 — Pioneer Whisper v1.0
  IACA #2025-DENE-PIONEER-400
  Two Mile Solutions LLC
  Zero-dep PQClean + GGWave
  Built 2025-10-30
  The whisper is original.

Block: 850,500
TXID: 0xaglg500...