"""
Backup Verification Tool
Ensures FlameChain backup integrity
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
                if name.startswith("data/resonance_logs/") and name.endswith(".json"):
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

def verify_backups(backup_dir: str = "backups") -> dict:
    """Verify all .zip backups in the backup directory."""
    if not os.path.exists(backup_dir):
        return {"error": f"Backup directory '{backup_dir}' not found"}

    backups = [f for f in os.listdir(backup_dir) if f.startswith("flamechain_backup_") and f.endswith(".zip")]
    report = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "backup_count": len(backups),
        "verified": [],
        "failed": [],
        "pi_checks": {},
        "total_size_mb": 0
    }

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
    report["status"] = "PASS" if not report["failed"] else "FAIL"
    return report

if __name__ == "__main__":
    import sys
    print("🔍 FlameChain Backup Verification")
    report = verify_backups(sys.argv[1] if len(sys.argv) > 1 else "backups")
    print(json.dumps(report, indent=2))
    if report.get("status") == "FAIL":
        sys.exit(1)
# Add to expected_hashes
expected_hashes = {
    "flame_anchor_protocol.md": hashlib.sha256(b"[Your manifest text]").hexdigest()  # Compute locally
}