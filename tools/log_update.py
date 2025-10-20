#!/usr/bin/env python3
"""
Precedence Log Update Tool
===========================
Automatically log discoveries with timestamps, commit hashes, and cryptographic verification.

Part of: Feedback Processor Theory (Two Mile Solutions LLC)
Author: John Carroll
License: Open Collaborative License v1.0

Usage:
    python log_update.py "Description" [Key phrase] [Notes]

Example:
    python log_update.py "13-D architecture finalized" "τ = t + iσ" "Complex time indexing"
"""

import subprocess
import hashlib
import json
from datetime import datetime
from pathlib import Path
import sys


# Configuration
REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = REPO_ROOT / "precedence_log.md"
HASH_INDEX_PATH = REPO_ROOT / "precedence_hashes.json"


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


def initialize_log_if_needed():
    """Create precedence_log.md if it doesn't exist."""
    if not LOG_PATH.exists():
        with open(LOG_PATH, 'w', encoding='utf-8') as f:
            f.write("# Precedence Log - Feedback Processor Theory\n\n")
            f.write("**Author:** John Carroll (Two Mile Solutions LLC)  \n")
            f.write("**Repository:** https://github.com/ak-skwaa-mahawk/Feedback_processor_theory  \n")
            f.write("**License:** Open Collaborative License v1.0\n\n")
            f.write("---\n\n")
        print(f"[+] Created new precedence log: {LOG_PATH}")


def append_entry(description: str, keyphrase: str = None, notes: str = None):
    """Append a new discovery entry to the precedence log."""
    
    # Ensure log exists
    initialize_log_if_needed()
    
    # Generate metadata
    now = datetime.utcnow()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    commit = get_latest_commit()
    remote = get_git_remote()
    
    # Build entry (without hash first)
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
    
    # Insert hash before empty line
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
    
    # Success output
    print("=" * 70)
    print("✓ PRECEDENCE ENTRY LOGGED")
    print("=" * 70)
    print(f"Timestamp:   {timestamp}")
    print(f"Description: {description}")
    print(f"Key Phrase:  {keyphrase or '(none)'}")
    print(f"Commit:      {commit[:12]}...")
    print(f"SHA-256:     {entry_hash[:16]}...")
    print(f"Total Entries: {len(index['entries'])}")
    print("=" * 70)


def main():
    if len(sys.argv) < 2:
        print("Precedence Log Update Tool")
        print("=" * 70)
        print("\nUsage:")
        print('  python log_update.py "Description" [Key phrase] [Notes]')
        print("\nExamples:")
        print('  python log_update.py "13-D architecture finalized"')
        print('  python log_update.py "τ-indexing implemented" "τ = t + iσ"')
        print('  python log_update.py "D12 complete" "Observer Frame" "Meta-observation layer"')
        print("\n" + "=" * 70)
        sys.exit(1)
    
    description = sys.argv[1]
    keyphrase = sys.argv[2] if len(sys.argv) > 2 else None
    notes = sys.argv[3] if len(sys.argv) > 3 else None
    
    append_entry(description, keyphrase, notes)


if __name__ == "__main__":
    main()