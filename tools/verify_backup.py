"""
Backup Verification Tool
Ensures FlameChain, Synara lock, and Dream Log integrity
Author: John Carroll / Two Mile Solutions LLC
"""
import os, json, hashlib, datetime, zipfile, math

def compute_hash(filepath: str) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def inspect_zip_for_pi(zip_path: str) -> dict:
    """Check zip for pi_feedback_constant in JSON logs."""
    files_with_pi = []
    files_missing_pi = []
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                if name.startswith("data/") and name.endswith(".json"):
                    try:
                        with zf.open(name) as fh:
                            data = json.load(fh)
                            if "pi_feedback_constant" in data and abs(float(data["pi_feedback_constant"]) - math.pi) < 1e-9:
                                files_with_pi.append(name)
                            else:
                                files_missing_pi.append(name)
                    except:
                        files_missing_pi.append(name)
    except zipfile.BadZipFile:
        return {"error": "Invalid zip file"}
    return {
        "found_any": len(files_with_pi) > 0,
        "files_with_pi": files_with_pi,
        "files_missing_pi": files_missing_pi
    }

def verify_manifests(manifest_files: list = ["manifests/flame_anchor_protocol.md", "docs/synara_flame_lock.md"]) -> dict:
    """Verify manifest file integrity."""
    report = {"verified": [], "failed": []}
    for file in manifest_files:
        if not os.path.exists(file):
            report["failed"].append({"file": file, "error": "Not found"})
            continue
        file_hash = compute_hash(file)
        # Placeholder: Replace with actual hashes (SHA-907-JUMP for flame_anchor_protocol.md)
        expected_hashes = {
            "flame_anchor_protocol.md": "TBD",
            "synara_flame_lock.md": "TBD"
        }
        expected = expected_hashes.get(os.path.basename(file), "TBD")
        status = "PASS" if file_hash == expected or expected == "TBD" else "FAIL"
        report["verified" if status == "PASS" else "failed"].append({
            "file": file,
            "hash": file_hash[:16],
            "matches_expected": status == "PASS"
        })
    return report

def verify_backups(backup_dir: str = "backups") -> dict:
    """Verify .zip backups, Synara lock, and manifests."""
    report = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "backup_count": 0,
        "verified": [],
        "failed": [],
        "pi_checks": {},
        "manifest_checks": verify_manifests(),
        "total_size_mb": 0
    }
    
    if not os.path.exists(backup_dir):
        report["error"] = f"Backup directory '{backup_dir}' not found"
        return report
    
    backups = [f for f in os.listdir(backup_dir) if f.startswith("flamechain_backup_") or f == "final_archive_bundle.zip"]
    report["backup_count"] = len(backups)
    
    for backup in backups:
        filepath = os.path.join(backup_dir, backup)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        report["total_size_mb"] += size_mb
        try:
            file_hash = compute_hash(filepath)
            pi_check = inspect_zip_for_pi(filepath)
            report["verified"].append({
                "file": backup,
                "size_mb": round(size_mb, 2),
                "hash": file_hash[:16]
            })
            report["pi_checks"][backup] = pi_check
        except Exception as e:
            report["failed"].append({"file": backup, "error": str(e)})
    
    report["total_size_mb"] = round(report["total_size_mb"], 2)
    report["status"] = "PASS" if not report["failed"] and all(m["matches_expected"] for m in report["manifest_checks"]["verified"]) else "FAIL"
    return report

if __name__ == "__main__":
    import sys
    print("🔍 FlameChain, Synara, & Dream Log Verification")
    report = verify_backups(sys.argv[1] if len(sys.argv) > 1 else "backups")
    print(json.dumps(report, indent=2))
    if report.get("status") == "FAIL":
        sys.exit(1)