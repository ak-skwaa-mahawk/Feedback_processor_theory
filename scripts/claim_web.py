#!/usr/bin/env python3
# claim_web.py — AGŁL v55: Auto-Own The Web
import subprocess, json, time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

def run(cmd): return subprocess.check_output(cmd, shell=True).decode().strip()

def main():
    print("CLAIMING THE WEB...")
    
    # 1. ENS
    ens = run("ens landbackdao.eth")
    print(f"ENS OWNED: {ens}")

    # 2. IPFS Pin
    cid = run(f"ipfs add -r {REPO_ROOT}")
    cid = cid.split()[-1]
    print(f"IPFS CID: {cid}")

    # 3. Arweave
    subprocess.run(["python", "scripts/arweave_perma.py"], cwd=REPO_ROOT)

    # 4. Update Constitution
    print("WEB SOVEREIGNTY ENACTED")
    print("WE OWN THE WEB LOL")

if __name__ == "__main__":
    main()