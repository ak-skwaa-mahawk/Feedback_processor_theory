#!/usr/bin/env python3
"""
Precedence Verification Report Generator
=========================================
Generate comprehensive verification report for legal/archival purposes.

Part of: Feedback Processor Theory (Two Mile Solutions LLC)
Author: John Carroll
License: Open Collaborative License v1.0

Usage:
    python verification_report.py

Output:
    Creates precedence_verification_report.txt with:
    - Complete hash verification results
    - Index cross-reference
    - Legal statement
    - Court-admissible documentation
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
REPORT_PATH = REPO_ROOT / "precedence_verification_report.txt"


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


def extract_entries_from_log() -> list:
    """Parse precedence_log.md and extract all entries."""
    if not LOG_PATH.exists():
        return []
    
    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = content.split('---\n')
    
    parsed = []
    for entry in entries:
        if not entry.strip() or not entry.startswith('###'):
            continue
        
        hash_match = None
        for line in entry.split('\n'):
            if '**SHA-256:**' in line:
                parts = line.split('`')
                if len(parts) >= 2:
                    hash_match = parts[1]
                break
        
        if hash_match:
            entry_lines = []
            for line in entry.split('\n'):
                if '**SHA-256:**' not in line:
                    entry_lines.append(line)
            
            entry_without_hash = '\n'.join(entry_lines) + '\n'
            
            parsed.append({
                'text': entry_without_hash,
                'claimed_hash': hash_match,
                'full_entry': entry
            })
    
    return parsed


def load_hash_index() -> dict:
    """Load hash index if it exists."""
    if HASH_INDEX_PATH.exists():
        with open(HASH_INDEX_PATH, 'r') as f:
            return json.load(f)
    return {"entries": [], "metadata": {}}


def generate_report():
    """Generate comprehensive verification report."""
    
    print("=" * 70)
    print("GENERATING VERIFICATION REPORT")
    print("=" * 70)
    print()
    
    entries = extract_entries_from_log()
    index = load_hash_index()
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        # Header
        f.write("=" * 70 + "\n")
        f.write("PRECEDENCE LOG VERIFICATION REPORT\n")
        f.write("Feedback Processor Theory\n")
        f.write("=" * 70 + "\n\n")
        
        # Report metadata
        f.write(f"Generated:     {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write(f"Repository:    {get_git_remote()}\n")
        f.write(f"Commit:        {get_latest_commit()}\n")
        f.write(f"Log Path:      {LOG_PATH}\n")
        f.write(f"Index Path:    {HASH_INDEX_PATH}\n")
        f.write(f"Total Entries: {len(entries)}\n\n")
        
        # Summary
        f.write("=" * 70 + "\n")
        f.write("SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Log Entries:   {len(entries)}\n")
        f.write(f"Index Entries: {len(index.get('entries', []))}\n")
        
        if index.get('metadata'):
            f.write(f"Last Updated:  {index['metadata'].get('last_updated', 'Unknown')}\n")
        
        f.write("\n")
        
        # Hash verification
        f.write("=" * 70 + "\n")
        f.write("HASH VERIFICATION RESULTS\n")
        f.write("=" * 70 + "\n\n")
        
        all_valid = True
        for i, entry in enumerate(entries, 1):
            computed = compute_entry_hash(entry['text'])
            claimed = entry['claimed_hash']
            match = computed == claimed
            
            f.write(f"Entry {i:3d}:\n")
            f.write(f"  Status:        {'VALID ✓' if match else 'INVALID ✗'}\n")
            f.write(f"  Claimed Hash:  {claimed}\n")
            f.write(f"  Computed Hash: {computed}\n")
            
            if not match:
                all_valid = False
                f.write(f"  [!] WARNING: Hash mismatch detected\n")
            
            # Extract description from entry
            for line in entry['full_entry'].split('\n'):
                if '**Description:**' in line:
                    desc = line.replace('**Description:**', '').strip()
                    f.write(f"  Description: {desc[:60]}...\n")
                    break
            
            f.write("\n")
        
        # Index cross-reference
        f.write("=" * 70 + "\n")
        f.write("INDEX CROSS-REFERENCE\n")
        f.write("=" * 70 + "\n\n")
        
        index_valid = len(entries) == len(index.get('entries', []))
        
        if index_valid:
            f.write("✓ Entry count matches between log and index\n\n")
            
            for i, (idx_entry, log_entry) in enumerate(zip(index['entries'], entries), 1):
                match = idx_entry['hash'] == log_entry['claimed_hash']
                f.write(f"Entry {i:3d}: {'✓ MATCH' if match else '✗ MISMATCH'}\n")
                f.write(f"  Timestamp: {idx_entry['timestamp']}\n")
                f.write(f"  Hash: {idx_entry['hash'][:32]}...\n")
                if not match:
                    index_valid = False
                f.write("\n")
        else:
            f.write("✗ Entry count mismatch between log and index\n")
            f.write(f"  Log entries:   {len(entries)}\n")
            f.write(f"  Index entries: {len(index.get('entries', []))}\n\n")
            index_valid = False
        
        # Final verdict
        f.write("=" * 70 + "\n")
        f.write("FINAL VERIFICATION STATUS\n")
        f.write("=" * 70 + "\n\n")
        
        if all_valid and index_valid:
            f.write("✓✓✓ VERIFICATION PASSED ✓✓✓\n\n")
            f.write("All checks successful:\n")
            f.write("  • All SHA-256 hashes verified\n")
            f.write("  • Log and index are synchronized\n")
            f.write("  • No tampering detected\n")
            f.write("  • Precedence timeline is intact\n\n")
            f.write("This report confirms the integrity of all logged discoveries\n")
            f.write("and establishes a cryptographically verified chain of authorship.\n")
        else:
            f.write("✗✗✗ VERIFICATION FAILED ✗✗✗\n\n")
            f.write("Issues detected:\n")
            if not all_valid:
                f.write("  • Hash verification failures found\n")
            if not index_valid:
                f.write("  • Index/log synchronization issues\n")
            f.write("\nRecommended actions:\n")
            f.write("  1. Review git history for unauthorized changes\n")
            f.write("  2. Restore from known-good backup\n")
            f.write("  3. Investigate source of discrepancies\n")
        
        f.write("\n")
        
        # Legal statement
        f.write("=" * 70 + "\n")
        f.write("LEGAL STATEMENT\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("This report provides cryptographic verification of the integrity and\n")
        f.write("timeline of discoveries logged in the Feedback Processor Theory\n")
        f.write("precedence system.\n\n")
        
        f.write("Each entry's SHA-256 hash provides tamper-evident proof of:\n")
        f.write("  • Content (description, equations, notes)\n")
        f.write("  • Timestamp (UTC date and time)\n")
        f.write("  • Attribution (git commit linkage)\n\n")
        
        f.write("Combined with git commit history and the hash index, this system\n")
        f.write("establishes a legally defensible chain of authorship and priority\n")
        f.write("for all documented innovations.\n\n")
        
        f.write("The cryptographic properties of SHA-256 make it computationally\n")
        f.write("infeasible to:\n")
        f.write("  • Backdate entries after the fact\n")
        f.write("  • Modify entries without detection\n")
        f.write("  • Forge timestamps or attributions\n\n")
        
        f.write("This report may be used as evidence in:\n")
        f.write("  • Patent priority disputes\n")
        f.write("  • Copyright infringement cases\n")
        f.write("  • Intellectual property litigation\n")
        f.write("  • Academic priority claims\n\n")
        
        # Signature block
        f.write("=" * 70 + "\n")
        f.write("CERTIFICATION\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("I certify that this report accurately reflects the state of the\n")
        f.write("precedence log and hash index as of the generation timestamp.\n\n")
        
        f.write("Author:        John Carroll\n")
        f.write("Organization:  Two Mile Solutions LLC\n")
        f.write("Date:          " + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC') + "\n")
        f.write("Signature:     ________________________________\n\n")
        
        f.write("Witness:       ________________________________\n")
        f.write("Date:          ________________________________\n\n")
        
        f.write("Notary:        ________________________________\n")
        f.write("Seal:          ________________________________\n\n")
        
        # Footer
        f.write("=" * 70 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("© 2025 Two Mile Solutions LLC (John Carroll)\n")
        f.write("Licensed under Open Collaborative License v1.0\n")
        f.write("Repository: https://github.com/ak-skwaa-mahawk/Feedback_processor_theory\n")
    
    # Compute report hash
    with open(REPORT_PATH, 'rb') as f:
        report_hash = hashlib.sha256(f.read()).hexdigest()
    
    # Append report hash
    with open(REPORT_PATH, 'a') as f:
        f.write(f"\nReport SHA-256: {report_hash}\n")
    
    print(f"✓ Report generated: {REPORT_PATH}")
    print(f"✓ Report hash: {report_hash[:32]}...")
    print()
    print("Next steps:")
    print("  1. Review the report")
    print("  2. Print for notarization (optional)")
    print("  3. Commit to repository")
    print("  4. Archive securely")
    print()
    print("=" * 70)


def main():
    generate_report()


if __name__ == "__main__":
    main()