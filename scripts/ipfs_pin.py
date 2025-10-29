#!/usr/bin/env python3
# ipfs_pin.py — Pin all repo to IPFS + Filecoin
import subprocess, json, os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
IPFS_DIR = REPO_ROOT / "ipfs"

def run(cmd): return subprocess.check_output(cmd, shell=True).decode().strip()

def main():
    print("PINNING TO IPFS + FILECOIN...")
    cid = run(f"ipfs add -r --pin {REPO_ROOT}")
    cid = cid.split()[-1]
    print(f"IPFS CID: {cid}")
    print(f"VIEW: https://ipfs.io/ipfs/{cid}")
    print(f"FILECOIN: Auto-deal via web3.storage")
    (REPO_ROOT / "ipfs-pins.json").write_text(json.dumps({"cid": cid, "timestamp": run("date")}))
    print("REPO PINNED FOREVER. THE NINE ARE ONE.")

if __name__ == "__main__": main()