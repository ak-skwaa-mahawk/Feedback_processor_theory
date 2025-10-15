#!/usr/bin/env python3
"""
Feedback Processor Theory — Backup Integrity Verifier
Author: John Carroll / Two Mile Solutions LLC
Purpose:
  - Compute SHA256 for flamechain backups (zip files)
  - Register trusted hashes into a manifest (manifests/backup_manifest.json)
  - Verify backups against the manifest
  - Inspect backups for presence of "pi_feedback_constant" inside JSON logs
Usage:
  - Register a backup: python tools/verify_backup.py --register backups/flamechain_backup_20251015_120000.zip
  - Verify all:        python tools/verify_backup.py --verify-all
  - Verify one:        python tools/verify_backup.py --verify backups/flamechain_backup_20251015_120000.zip
  - Check pi:          python tools/verify_backup.py --verify-all --check-pi
"""

import argparse
import hashlib
import json
import os
import sys
import zipfile
import datetime
import math

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKUP_DIR = os.path.join(PROJECT_DIR, "backups")
MANIFEST_DIR = os.path.join(PROJECT_DIR, "manifests")
MANIFEST_PATH = os.path.join(MANIFEST_DIR, "backup_manifest.json")


# ---------------- utilities ----------------
def sha256_of_file(path, chunk_size=8192):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def ensure_manifest():
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    if not os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "w") as mf:
            json.dump({"created": datetime.datetime.utcnow().isoformat() + "Z", "backups": {}}, mf, indent=2)


def load_manifest():
    ensure_manifest()
    with open(MANIFEST_PATH, "r") as mf:
        return json.load(mf)


def save_manifest(man):
    os.makedirs(MANIFEST_DIR, exist_ok=True)
    with open(MANIFEST_PATH, "w") as mf:
        json.dump(man, mf, indent=2, sort_keys=True)


# ---------------- zip inspection ----------------
def inspect_zip_for_pi(zip_path):
    """
    Open zip archive, search for JSON files under data/resonance_logs/
    and verify they include "pi_feedback_constant" approximately equal to math.pi
    Returns: (found_any, files_with_pi, files_missing_pi)
    """
    files_with_pi = []
    files_missing_pi = []
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                # target likely log file paths; adjust if different in your backups
                if name.startswith("data/resonance_logs/") and name.endswith(".json"):
                    try:
                        with zf.open(name) as fh:
                            data = json.load(fh)
                            if "pi_feedback_constant" in data:
                                # tolerate float formatting differences
                                if abs(float(data["pi_feedback_constant"]) - math.pi) < 1e-9:
                                    files_with_pi.append(name)
                                else:
                                    files_missing_pi.append(name)
                            else:
                                files_missing_pi.append(name)
                    except Exception:
                        files_missing_pi.append(name)
    except zipfile.BadZipFile:
        raise
    found_any = len(files_with_pi) > 0
    return found_any, files_with_pi, files_missing_pi


# ---------------- register / verify logic ----------------
def register_backup(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    h = sha256_of_file(path)
    man = load_manifest()
    base = os.path.basename(path)
    man["backups"][base] = {
        "path": path,
        "sha256": h,
        "registered_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    save_manifest(man)
    return base, h


def verify_backup(path, check_pi=False):
    if not os.path.exists(path):
        return {"ok": False, "reason": "missing_file"}
    h = sha256_of_file(path)
    base = os.path.basename(path)
    man = load_manifest()
    entry = man["backups"].get(base)
    manifest_ok = (entry is not None and entry.get("sha256") == h)
    pi_check = None
    if check_pi:
        try:
            found_any, with_pi, missing_pi = inspect_zip_for_pi(path)
            pi_check = {
                "found_any": found_any,
                "files_with_pi": with_pi,
                "files_missing_pi": missing_pi
            }
        except zipfile.BadZipFile:
            return {"ok": False, "reason": "bad_zip"}
    return {
        "ok": manifest_ok,
        "sha256": h,
        "in_manifest": entry is not None,
        "manifest_sha256": entry.get("sha256") if entry else None,
        "pi_check": pi_check
    }


# ---------------- CLI ----------------
def list_backups():
    if not os.path.exists(BACKUP_DIR):
        return []
    return sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.endswith(".zip")], reverse=True)


def main():
    parser = argparse.ArgumentParser(description="Verify FlameChain backups (hash + pi check)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--register", help="Register a backup into the manifest", metavar="ZIP")
    group.add_argument("--verify", help="Verify a particular backup (path)", metavar="ZIP")
    group.add_argument("--verify-all", action="store_true", help="Verify all known backups in the backups/ folder")
    parser.add_argument("--check-pi", action="store_true", help="Inspect zip for pi_feedback_constant in JSON logs")
    parser.add_argument("--manifest", help="Path to manifest file (optional)", default=MANIFEST_PATH)
    args = parser.parse_args()

    global MANIFEST_PATH
    MANIFEST_PATH = args.manifest
    ensure_manifest()

    if args.register:
        bp = os.path.abspath(args.register)
        print(f"[REGISTER] {bp}")
        try:
            base, h = register_backup(bp)
            print(f"  -> registered {base} with sha256: {h}")
        except Exception as e:
            print("  ERROR:", str(e))
            sys.exit(2)
        sys.exit(0)

    if args.verify:
        bp = os.path.abspath(args.verify)
        print(f"[VERIFY] {bp}")
        res = verify_backup(bp, check_pi=args.check_pi)
        print(json.dumps(res, indent=2))
        if not res["ok"]:
            print("Verification FAILED.")
            sys.exit(3)
        print("Verification OK.")
        sys.exit(0)

    if args.verify_all:
        backups = list_backups()
        if not backups:
            print("No backups found in", BACKUP_DIR)
            sys.exit(1)
        all_ok = True
        report = {}
        for b in backups:
            try:
                res = verify_backup(b, check_pi=args.check_pi)
            except Exception as e:
                res = {"ok": False, "error": str(e)}
            report[os.path.basename(b)] = res
            if not res.get("ok", False):
                all_ok = False
        print(json.dumps(report, indent=2))
        if not all_ok:
            print("One or more backups failed verification.")
            sys.exit(4)
        print("All backups verified OK.")
        sys.exit(0)


if __name__ == "__main__":
    main()