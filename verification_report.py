#!/usr/bin/env python3
"""
Precedence Logging & Verification System
=========================================
Automatically log discoveries with timestamps, commit hashes, and cryptographic verification.

Part of: Feedback Processor Theory (Two Mile Solutions LLC)
Author: John Carroll
License: Open Collaborative License v1.0
"""

import subprocess
import hashlib
import json
from datetime import datetime
from pathlib import Path
import sys


# ============================================================================
# CONFIGURATION
# ============================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = REPO_ROOT / "precedence_log.md"
HASH_INDEX_PATH = REPO_ROOT / "precedence_hashes.json"


# ============================================================================
# LOG_UPDATE.PY - Main Precedence Logger
# ============================================================================

def get_latest_commit():
    """Get latest commit hash from git."""
    try:
        result = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            stderr=subprocess.DEVNULL
        )
        return result.decode("utf-8").strip()
    except Exception:
        return "unknown-commit"


def get_git_remote():
    """Get git remote URL."""
    try:
        result = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=REPO_ROOT,
            stderr=subprocess.DEVNULL
        )
        return result.decode("utf-8").strip()
    except Exception:
        return "unknown-remote"


def compute_entry_hash(entry_text: str) -> str:
    """Compute SHA-256 hash of entry for verification."""
    return hashlib.sha256(entry_text.encode('utf-8')).hexdigest()


def load_hash_index() -> dict:
    """Load existing hash index or create new one."""
    if HASH_INDEX_PATH.exists():
        with open(HASH_INDEX_PATH, 'r') as f:
            return json.load(f)
    return {"entries": [], "metadata": {}}


def save_hash_index(index: dict):
    """Save hash index to file."""
    with open(HASH_INDEX_PATH, 'w') as f:
        json.dump(index, f, indent=2)


def append_entry(description: str, keyphrase: str = None, notes: str = None):
    """Append a new discovery entry to the precedence log."""
    
    # Generate metadata
    now = datetime.utcnow()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    commit = get_latest_commit()
    remote = get_git_remote()
    
    # Build entry
    entry_lines = [
        f"### [{timestamp}] — Discovery",
        f"**Description:** {description}",
        f"**Key Phrase/Equation:** {keyphrase or '(none)'}",
        f"**Reference Commit:** `{commit}`",
        f"**Repository:** {remote}",
        f"**Notes:** {notes or '(none)'}",
        ""
    ]
    
    entry_text = "\n".join(entry_lines)
    
    # Compute hash
    entry_hash = compute_entry_hash(entry_text)
    entry_lines.insert(-1, f"**SHA-256:** `{entry_hash}`")
    entry_text_with_hash = "\n".join(entry_lines)
    
    # Append to log
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry_text_with_hash)
        f.write("\n---\n\n")
    
    # Update hash index
    index = load_hash_index()
    index["entries"].append({
        "timestamp": timestamp,
        "description": description,
        "keyphrase": keyphrase,
        "commit": commit,
        "hash": entry_hash,
        "unix_time": int(now.timestamp())
    })
    index["metadata"]["last_updated"] = timestamp
    index["metadata"]["total_entries"] = len(index["entries"])
    save_hash_index(index)
    
    print(f"[✓] Entry added to {LOG_PATH.name}")
    print(f"[✓] Timestamp: {timestamp}")
    print(f"[✓] Commit: {commit[:8]}...")
    print(f"[✓] SHA-256: {entry_hash[:16]}...")
    print(f"[✓] Hash index updated: {len(index['entries'])} total entries")


# ============================================================================
# VERIFY_LOG_HASH.PY - Hash Verification Tool
# ============================================================================

def extract_entries_from_log() -> list:
    """Parse precedence_log.md and extract all entries."""
    if not LOG_PATH.exists():
        return []
    
    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by separator
    entries = content.split('---\n')
    
    parsed = []
    for entry in entries:
        if not entry.strip() or not entry.startswith('###'):
            continue
        
        # Extract hash if present
        hash_match = None
        for line in entry.split('\n'):
            if '**SHA-256:**' in line:
                hash_match = line.split('`')[1] if '`' in line else None
                break
        
        if hash_match:
            # Remove hash line for recomputation
            entry_without_hash = '\n'.join([
                line for line in entry.split('\n')
                if '**SHA-256:**' not in line
            ]) + '\n'
            
            parsed.append({
                'text': entry_without_hash,
                'claimed_hash': hash_match,
                'full_entry': entry
            })
    
    return parsed


def verify_all_hashes():
    """Verify all SHA-256 hashes in the precedence log."""
    print("=" * 70)
    print("PRECEDENCE LOG HASH VERIFICATION")
    print("=" * 70)
    print()
    
    entries = extract_entries_from_log()
    
    if not entries:
        print("[!] No entries found in precedence log")
        return False
    
    print(f"Found {len(entries)} entries to verify\n")
    
    all_valid = True
    for i, entry in enumerate(entries, 1):
        computed = compute_entry_hash(entry['text'])
        claimed = entry['claimed_hash']
        
        match = computed == claimed
        symbol = "✓" if match else "✗"
        
        print(f"Entry {i}: {symbol} {'VALID' if match else 'INVALID'}")
        print(f"  Claimed:  {claimed}")
        print(f"  Computed: {computed}")
        
        if not match:
            all_valid = False
            print(f"  [!] HASH MISMATCH - Entry may have been tampered with!")
        
        print()
    
    print("=" * 70)
    if all_valid:
        print("✓ ALL HASHES VERIFIED - Log integrity confirmed")
    else:
        print("✗ VERIFICATION FAILED - Some entries have invalid hashes")
    print("=" * 70)
    
    return all_valid


def verify_against_index():
    """Cross-reference log entries with hash index."""
    print("\n" + "=" * 70)
    print("CROSS-REFERENCING WITH HASH INDEX")
    print("=" * 70)
    print()
    
    if not HASH_INDEX_PATH.exists():
        print("[!] Hash index not found")
        return False
    
    index = load_hash_index()
    log_entries = extract_entries_from_log()
    
    print(f"Index entries: {len(index['entries'])}")
    print(f"Log entries: {len(log_entries)}")
    print()
    
    if len(index['entries']) != len(log_entries):
        print("[!] Count mismatch between index and log")
        return False
    
    all_match = True
    for i, (idx_entry, log_entry) in enumerate(zip(index['entries'], log_entries), 1):
        match = idx_entry['hash'] == log_entry['claimed_hash']
        symbol = "✓" if match else "✗"
        
        print(f"Entry {i}: {symbol} {'MATCH' if match else 'MISMATCH'}")
        print(f"  Index:    {idx_entry['hash'][:32]}...")
        print(f"  Log:      {log_entry['claimed_hash'][:32]}...")
        print(f"  Timestamp: {idx_entry['timestamp']}")
        
        if not match:
            all_match = False
        
        print()
    
    if all_match:
        print("✓ INDEX VERIFICATION COMPLETE - All entries match")
    else:
        print("✗ INDEX VERIFICATION FAILED - Discrepancies detected")
    
    return all_match


def export_verification_report():
    """Generate a verification report for legal/archival purposes."""
    report_path = REPO_ROOT / "precedence_verification_report.txt"
    
    with open(report_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("PRECEDENCE LOG VERIFICATION REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write(f"Repository: {get_git_remote()}\n")
        f.write(f"Commit: {get_latest_commit()}\n")
        f.write(f"Log Path: {LOG_PATH}\n")
        f.write(f"Index Path: {HASH_INDEX_PATH}\n\n")
        
        # Verify log hashes
        entries = extract_entries_from_log()
        f.write(f"Total Entries: {len(entries)}\n\n")
        
        f.write("HASH VERIFICATION:\n")
        f.write("-" * 70 + "\n")
        
        all_valid = True
        for i, entry in enumerate(entries, 1):
            computed = compute_entry_hash(entry['text'])
            claimed = entry['claimed_hash']
            match = computed == claimed
            
            f.write(f"\nEntry {i}:\n")
            f.write(f"  Status: {'VALID' if match else 'INVALID'}\n")
            f.write(f"  Claimed Hash:  {claimed}\n")
            f.write(f"  Computed Hash: {computed}\n")
            
            if not match:
                all_valid = False
                f.write(f"  [!] WARNING: Hash mismatch detected\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("FINAL VERIFICATION STATUS: ")
        f.write("PASSED - All hashes verified\n" if all_valid else "FAILED - Hash discrepancies found\n")
        f.write("=" * 70 + "\n\n")
        
        # Add legal statement
        f.write("LEGAL STATEMENT:\n")
        f.write("-" * 70 + "\n")
        f.write("This report cryptographically verifies the integrity and timeline of\n")
        f.write("discoveries logged in the Feedback Processor Theory precedence log.\n")
        f.write("Each entry's SHA-256 hash provides tamper-evident proof of content and\n")
        f.write("timestamp. Combined with git commit history, this establishes a legally\n")
        f.write("defensible chain of authorship and priority.\n\n")
        f.write("© 2025 Two Mile Solutions LLC (John Carroll)\n")
        f.write("All entries subject to Open Collaborative License v1.0\n")
    
    print(f"\n[✓] Verification report saved to: {report_path}")
    return report_path


def print_latest_entry():
    """Display the most recent log entry."""
    index = load_hash_index()
    
    if not index.get('entries'):
        print("[!] No entries in log")
        return
    
    latest = index['entries'][-1]
    
    print("\n" + "=" * 70)
    print("LATEST PRECEDENCE ENTRY")
    print("=" * 70)
    print(f"Timestamp:   {latest['timestamp']}")
    print(f"Description: {latest['description']}")
    print(f"Key Phrase:  {latest.get('keyphrase', '(none)')}")
    print(f"Commit:      {latest['commit']}")
    print(f"SHA-256:     {latest['hash']}")
    print(f"Total Entries: {len(index['entries'])}")
    print("=" * 70)


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

def main():
    if len(sys.argv) < 2:
        print("Precedence Logging & Verification System")
        print("=" * 70)
        print("\nUsage:")
        print('  Add entry:     python tools/log_update.py "Description" [Key phrase] [Notes]')
        print('  Verify hashes: python tools/verify_log_hash.py')
        print('  Latest entry:  python tools/latest_entry.py')
        print('  Full report:   python tools/verification_report.py')
        print("\nExamples:")
        print('  python tools/log_update.py "13-D architecture finalized" "τ = t + iσ"')
        print('  python tools/verify_log_hash.py')
        sys.exit(1)
    
    command = Path(sys.argv[0]).stem
    
    if command == "log_update":
        description = sys.argv[1]
        keyphrase = sys.argv[2] if len(sys.argv) > 2 else None
        notes = sys.argv[3] if len(sys.argv) > 3 else None
        append_entry(description, keyphrase, notes)
    
    elif command == "verify_log_hash":
        valid = verify_all_hashes()
        verify_against_index()
        sys.exit(0 if valid else 1)
    
    elif command == "verification_report":
        export_verification_report()
    
    elif command == "latest_entry":
        print_latest_entry()
    
    else:
        print(f"[!] Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()