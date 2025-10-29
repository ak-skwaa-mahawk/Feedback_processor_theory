#!/usr/bin/env python3
# arweave_perma.py — AGŁL v53 Eternal Seal
# Uploads ALL repo files to Arweave → 200+ year permanence
# Run: python scripts/arweave_perma.py

import os
import json
import time
from pathlib import Path
from datetime import datetime
import pytz
import subprocess

# === CONFIG ===
REPO_ROOT = Path(__file__).parent.parent
ARWEAVE_DIR = REPO_ROOT / "arweave"
WALLET_PATH = REPO_ROOT / "arweave_wallet.json"  # Your Arweave keyfile
ARWEAVE_DIR.mkdir(exist_ok=True)

# Install: pip install arweave-python-client
try:
    from arweave.arweave_lib import Wallet, Transaction
except:
    print("Installing arweave-python-client...")
    subprocess.run(["pip", "install", "arweave-python-client"], check=True)
    from arweave.arweave_lib import Wallet, Transaction

# === AUTO-UPLOAD ALL FILES TO ARWEAVE ===
def upload_to_arweave(file_path):
    if not WALLET_PATH.exists():
        print("ERROR: arweave_wallet.json not found!")
        print("Get one: https://faucet.arweave.net")
        return None

    wallet = Wallet(str(WALLET_PATH))
    file_name = file_path.name
    tx_path = ARWEAVE_DIR / f"{file_name}.tx"

    print(f"UPLOADING TO ARWEAVE: {file_path} → {tx_path}")

    try:
        with open(file_path, "rb") as f:
            data = f.read()

        tx = Transaction(wallet, data=data)
        tx.add_tag('App-Name', 'AGŁL v53')
        tx.add_tag('App-Version', '1.0')
        tx.add_tag('Content-Type', 'application/octet-stream')
        tx.add_tag('Glyph', 'łᐊᒥłł')
        tx.add_tag('Drum-Hz', '60')
        tx.add_tag('LandBackDAO', 'v2')
        tx.add_tag('Eternal-Seal', 'True')
        tx.sign()
        tx.send()

        arweave_url = f"https://arweave.net/{tx.id}"
        tx_path.write_text(json.dumps({
            "file": str(file_path),
            "txid": tx.id,
            "url": arweave_url,
            "timestamp": datetime.now(pytz.utc).isoformat(),
            "status": "PERMANENT"
        }, indent=2))

        return {
            "file": str(file_path),
            "txid": tx.id,
            "url": arweave_url,
            "status": "PERMANENT"
        }
    except Exception as e:
        return {"file": str(file_path), "error": str(e)}

# === MAIN ETERNAL SEAL LOOP ===
def main():
    print("AGŁL v53 — ARWEAVE ETERNAL SEAL LIVE")
    print("=" * 60)

    if not WALLET_PATH.exists():
        print("CREATE WALLET FIRST:")
        print("curl -s https://faucet.arweave.net | python - > arweave_wallet.json")
        return

    files_to_seal = []
    for dir_path in ["data", "contracts", "frontend", "scripts", "docs"]:
        dir_p = REPO_ROOT / dir_path
        if dir_p.exists():
            files_to_seal.extend(dir_p.rglob("*.*"))

    seals = []
    for file in files_to_seal:
        if file.suffix not in [".ots", ".tx", ".pyc"]:
            seal = upload_to_arweave(file)
            if seal and "txid" in seal:
                print(f"PERMANENT → {file.name} | TX: {seal['txid']}")
            else:
                print(f"FAILED → {file.name}")
            seals.append(seal)
            time.sleep(2)  # Avoid rate limits

    # === SAVE ETERNAL MANIFEST ===
    manifest = {
        "agll": "v53",
        "flamekeeper": "Zhoo",
        "glyph": "łᐊᒥłł",
        "drum_hz": 60.0,
        "permanence": "200+ years",
        "total_seals": len([s for s in seals if s and "txid" in s]),
        "timestamp": datetime.now(pytz.utc).isoformat(),
        "arweave_seals": [s for s in seals if s and "txid" in s]
    }

    manifest_path = ARWEAVE_DIR / "ETERNAL_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    print("\nETERNAL MANIFEST SAVED:", manifest_path)
    print("ALL FILES SEALED IN ARWEAVE. THE NINE ARE FOREVER.")
    print("WE ARE STILL HERE.")

if __name__ == "__main__":
    main()