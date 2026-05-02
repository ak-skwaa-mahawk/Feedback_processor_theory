#!/usr/bin/env python3
"""
tools/repair_ledger_viewer.py — Sovereign Repair Ledger Tailer
Shows only CODE_REPAIR events with ECDSA receipt status + glyph before/after
"""

import json
import time
from pathlib import Path
from ecdsa import VerifyingKey, SECP256k1

LOG_PATH = Path("rmp_log.jsonl")
VK = None  # Will load from rmp_key.pem if present

def load_verifying_key():
    global VK
    keypath = Path("rmp_key.pem")
    if keypath.exists():
        try:
            sk = open(keypath).read()
            VK = VerifyingKey.from_pem(sk)
        except:
            pass

def verify_receipt(record):
    if "receipt" not in record or not VK:
        return "⚠️  No receipt / key"
    try:
        payload = {k: v for k, v in record.items() if k != "receipt"}
        sig = bytes.fromhex(record["receipt"])
        return "✅ Verified" if VK.verify(sig, json.dumps(payload, sort_keys=True).encode()) else "❌ Invalid"
    except:
        return "❌ Verify failed"

def tail_repair_ledger():
    load_verifying_key()
    print("🔧 Sovereign Repair Ledger Viewer — watching rmp_log.jsonl\n")
    print(f"{'Time':<20} {'File':<40} {'Coherence':<10} {'Glyph Before → After':<50} {'Receipt'}")
    print("-" * 130)

    with open(LOG_PATH, "r") as f:
        f.seek(0, 2)  # tail
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            try:
                record = json.loads(line.strip())
                if record.get("event") != "CODE_REPAIR":
                    continue

                ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record["ts"]))
                file = record["file"]
                coh = f"{record.get('coherence', 0):.2f}"
                glyph_before = record.get("originalglyph", "—")[:8]
                glyph_after = record.get("newglyph", "—")[:8]
                status = verify_receipt(record)

                print(f"{ts:<20} {file:<40} {coh:<10} {glyph_before} → {glyph_after:<40} {status}")
            except:
                continue

if __name__ == "__main__":
    tail_repair_ledger()