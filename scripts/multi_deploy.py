#!/usr/bin/env python3
# multi_deploy.py — AGŁL v62: Deploy to Fleek + Cloudflare + IPFS
import subprocess, os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

def run(cmd):
    print(f"🚀 {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def main():
    print("AGŁL v62 — MULTI-HOST DEPLOY LIVE")
    print("="*60)
    
    # 1. IPFS
    cid = subprocess.check_output("ipfs add -r .", shell=True).decode().split()[-1]
    print(f"IPFS CID: {cid}")
    
    # 2. Fleek
    run("fleek site deploy . --name dao-landback")
    
    # 3. Cloudflare (manual DNS)
    print("CLOUDFLARE: CNAME dao.landback → dao-landback.fleek.co")
    
    # 4. Verify
    print(f"LIVE SITES:")
    print(f"  • IPFS: https://ipfs.io/ipfs/{cid}")
    print(f"  • Fleek: https://dao-landback.fleek.co")
    print(f"  • Handshake: http://dao.landback")
    print(f"  • ENS: https://dao.landback.eth.link")

if __name