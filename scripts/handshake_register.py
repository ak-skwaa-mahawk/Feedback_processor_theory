#!/usr/bin/env python3
# handshake_register.py — AGŁL v56: Auto-Register Handshake TLDs
import json, time, subprocess, os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WALLET = REPO_ROOT / "handshake/wallet.json"
BIDS = REPO_ROOT / "handshake/bids"

BIDS.mkdir(exist_ok=True)

TLDS = ["landback", "denali", "sachoo", "ninestars", "agll", "dene"]

def hns_cli(cmd):
    return subprocess.check_output(f"hns {cmd}", shell=True).decode().strip()

def main():
    print("RECLAIMING THE ROOT ZONE...")
    
    if not WALLET.exists():
        print("GENERATING HANDSHAKE WALLET...")
        hns_cli("wallet create --password=agll2025")
        print("WALLET CREATED. FUND WITH HNS.")

    for tld in TLDS:
        bid_file = BIDS / f"{tld}.json"
        if not bid_file.exists():
            print(f"BIDDING ON .{tld}")
            bid = hns_cli(f"auction bid {tld} 1000 --lockup 10000")
            bid_file.write_text(json.dumps({
                "tld": tld,
                "bid_hns": 1000,
                "lockup_hns": 10000,
                "status": "bidding",
                "timestamp": time.time()
            }))
            print(f".{tld} → BID PLACED")
        else:
            data = json.loads(bid_file.read_text())
            if data["status"] == "bidding":
                print(f".{tld} → REVEAL PENDING")
            else:
                print(f".{tld} → OWNED BY TWO MILE LLC")

    print("HANDSHAKE ROOT RECLAIMED. THE WEB IS OURS.")

if __name__ == "__main__":
    main()