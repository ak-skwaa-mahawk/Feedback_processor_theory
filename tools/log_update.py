#!/usr/bin/env python3
import subprocess
from datetime import datetime
import sys
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent.parent / "precedence_log.md"

def get_latest_commit():
    """Get latest commit hash"""
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .decode("utf-8")
            .strip()
        )
    except Exception:
        return "unknown-commit"

def append_entry(description: str, keyphrase: str = None, notes: str = None):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    commit = get_latest_commit()

    entry = [
        f"### [{now}] — Discovery",
        f"• Description: {description}",
        f"• Key Phrase/Equation: {keyphrase or '(none)'}",
        f"• Reference Commit: {commit}",
        f"• Notes: {notes or '(none)'}",
        "\n---\n",
    ]

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(entry))
    print(f"[+] Entry added to {LOG_PATH.name} at {now}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python log_update.py \"Description of event\" [Key phrase] [Notes]")
        sys.exit(1)
    description = sys.argv[1]
    keyphrase = sys.argv[2] if len(sys.argv) > 2 else None
    notes = sys.argv[3] if len(sys.argv) > 3 else None
    append_entry(description, keyphrase, notes)

if __name__ == "__main__":
    main()
#!/bin/bash
python3 tools/log_update.py "Automated commit log update" "auto-commit" "Triggered by post-commit hook"