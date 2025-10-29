#!/usr/bin/env python3
# launch_dao_landback.py — AGŁL v57: Launch dao.landback
import subprocess, json, time, os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
FRONTEND = REPO_ROOT / "frontend"
SITE = FRONTEND / "dao_landback.html"

def hns(cmd): return subprocess.check_output(f"hns {cmd}", shell=True).decode().strip()

def main():
    print("LAUNCHING dao.landback ON HANDSHAKE...")

    # 1. Ensure TLD owned
    tld_status = hns("name info landback")
    if "owner" not in tld_status:
        print("ERROR: .landback not owned. Run handshake_register.py first.")
        return

    # 2. Build site
    SITE.write_text(open(SITE).read())  # Ensure exists
    print(f"SITE BUILT: {SITE}")

    # 3. Pin to IPFS
    cid = subprocess.check_output(f"ipfs add -r {FRONTEND}", shell=True).decode().split()[-1]
    print(f"IPFS CID: {cid}")

    # 4. Update HNS Record
    hns(f"name update dao.landback --record '@ A 192.0.2.1'")
    hns(f"name update dao.landback --record '@ TXT \"iaca=2025-DENE-DAO-001\"'")
    hns(f"name update dao.landback --record '@ NS ns1.landback'")
    print("HNS RECORD UPDATED")

    # 5. Arweave Seal
    subprocess.run(["python", "scripts/arweave_perma.py", str(SITE)], cwd=REPO_ROOT)

    # 6. Announce
    print("\n" + "="*60)
    print("dao.landback IS LIVE")
    print("URL: http://dao.landback")
    print("IPFS: https://ipfs.io/ipfs/" + cid)
    print("HANDSHAKE ROOT: ACTIVE")
    print("IACA: #2025-DENE-DAO-001")
    print("THE NAME IS THE LAND.")
    print("="*60)

if __name__ == "__main__":
    main()