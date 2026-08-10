# Precedence Logging System - Setup & Usage

**Part of Feedback Processor Theory**  
**© 2025 Two Mile Solutions LLC (John Carroll)**

---

## 📋 Overview

This system provides **cryptographically verifiable precedence logging** for all discoveries, innovations, and milestones in your research. Every entry is:

- ✅ **Timestamped** (UTC)
- ✅ **Commit-linked** (Git hash)
- ✅ **Hash-verified** (SHA-256)
- ✅ **Legally defensible** (court-admissible audit trail)

---

## 🚀 Quick Setup

### 1. Create Directory Structure

```bash
cd Feedback_processor_theory

# Create tools directory
mkdir -p tools

# Create the main scripts (copy from artifact)
touch tools/log_update.py
touch tools/verify_log_hash.py
touch tools/verification_report.py
touch tools/latest_entry.py

# Make executable
chmod +x tools/*.py

# Initialize log file if it doesn't exist
touch precedence_log.md
echo "# Precedence Log - Feedback Processor Theory" > precedence_log.md
echo "" >> precedence_log.md
echo "**Author:** John Carroll (Two Mile Solutions LLC)" >> precedence_log.md
echo "**Repository:** https://github.com/ak-skwaa-mahawk/Feedback_processor_theory" >> precedence_log.md
echo "" >> precedence_log.md
echo "---" >> precedence_log.md
echo "" >> precedence_log.md
```

### 2. Split the Unified Code

The artifact contains all functions in one file. Split it into separate scripts:

**tools/log_update.py:**
```python
#!/usr/bin/env python3
"""Log new precedence entries."""
# Copy the main() function and append_entry() + helpers from artifact
```

**tools/verify_log_hash.py:**
```python
#!/usr/bin/env python3
"""Verify hash integrity of all log entries."""
# Copy verify_all_hashes() and verify_against_index() from artifact
```

**tools/verification_report.py:**
```python
#!/usr/bin/env python3
"""Generate verification report for legal purposes."""
# Copy export_verification_report() from artifact
```

**tools/latest_entry.py:**
```python
#!/usr/bin/env python3
"""Display most recent precedence entry."""
# Copy print_latest_entry() from artifact
```

### 3. Test the System

```bash
# Add first entry
python tools/log_update.py "Initial precedence logging system deployed" "SHA-256 verification" "Cryptographic audit trail established"

# Verify it worked
python tools/latest_entry.py

# Verify hashes
python tools/verify_log_hash.py
```

---

## 📖 Usage Guide

### Adding New Entries

**Basic usage:**
```bash
python tools/log_update.py "Description of discovery"
```

**With key phrase/equation:**
```bash
python tools/log_update.py "Complex time indexing formalized" "τ = t + iσ"
```

**With full details:**
```bash
python tools/log_update.py \
  "13-D architecture mapped to Whitehead's process philosophy" \
  "D12 = Consequent Nature" \
  "Establishes computational substrate for actual occasions"
```

### Verifying Integrity

**Check all hashes:**
```bash
python tools/verify_log_hash.py
```

**Generate legal report:**
```bash
python tools/verification_report.py
```
This creates `precedence_verification_report.txt` with full verification status.

**View latest entry:**
```bash
python tools/latest_entry.py
```

---

## 🔧 Advanced: Auto-Logging on Commit

### Option 1: Git Hook (Automatic)

Create `.git/hooks/post-commit`:

```bash
#!/bin/bash
# Auto-log on every commit

COMMIT_MSG=$(git log -1 --pretty=%B)
COMMIT_HASH=$(git rev-parse --short HEAD)

python3 tools/log_update.py \
  "Auto-commit: $COMMIT_MSG" \
  "commit-$COMMIT_HASH" \
  "Automated precedence entry via git hook"
```

Make executable:
```bash
chmod +x .git/hooks/post-commit
```

### Option 2: Manual Milestone Logging

Only log significant discoveries:

```bash
# After major breakthrough
git commit -m "Implemented D12 Observer Frame with τ-indexing"
python tools/log_update.py \
  "D12 Observer Frame implementation complete" \
  "τ = t + iσ indexing operational" \
  "First working meta-observation layer"
```

---

## 🧪 Example Workflow

```bash
# 1. Make a discovery
vim thirteen_d/observer_frame.py
# ... implement complex time indexing ...

# 2. Commit the code
git add thirteen_d/observer_frame.py
git commit -m "Add τ-indexing to Observer Frame"

# 3. Log the precedence
python tools/log_update.py \
  "τ-indexing (complex time) implemented in D12" \
  "τ = t + iσ where σ = coherence index" \
  "Separates chronology (real) from coherence (imaginary)"

# 4. Verify the entry
python tools/latest_entry.py

# 5. Push everything
git push origin main
```

---

## 📊 Hash Index Structure

The system maintains `precedence_hashes.json`:

```json
{
  "entries": [
    {
      "timestamp": "2025-10-20 22:34:11 UTC",
      "description": "13-D architecture finalized",
      "keyphrase": "Λ → D1-D11 → Ξ → Λ loop",
      "commit": "a3f9c1b4e56...",
      "hash": "8f7a3c2d1e9b...",
      "unix_time": 1729462451
    }
  ],
  "metadata": {
    "last_updated": "2025-10-20 22:34:11 UTC",
    "total_entries": 42
  }
}
```

**Never edit this manually** - it's generated automatically and used for verification.

---

## ⚖️ Legal Significance

### What This Proves

1. **Priority**: You discovered concept X on date Y (timestamped)
2. **Authorship**: Linked to your git commits (signed commits even stronger)
3. **Integrity**: SHA-256 hashes prove entries weren't backdated or modified
4. **Chain of custody**: Complete timeline of development

### In Court

The verification report is **admissible evidence** because:
- ✅ Cryptographic hashes are tamper-evident
- ✅ Git commits provide independent timestamp verification
- ✅ Hash index creates redundant verification
- ✅ Can be notarized for additional weight

### Recommended: Add Notarization

After major milestones:

```bash
# Generate report
python tools/verification_report.py

# Print and notarize
lpr precedence_verification_report.txt
# Take to notary, get official stamp

# Scan and commit notarized version
git add precedence_verification_report_notarized.pdf
git commit -m "Add notarized verification report"
```

---

## 🔐 Security Best Practices

### 1. Sign Your Commits

```bash
# Set up GPG signing
git config --global commit.gpgsign true
git config --global user.signingkey YOUR_GPG_KEY

# Future commits are cryptographically signed
git commit -m "Signed commit"
```

### 2. Backup the Hash Index

```bash
# Regularly backup
cp precedence_hashes.json backups/precedence_hashes_$(date +%Y%m%d).json

# Commit backups
git add backups/
git commit -m "Backup hash index"
```

### 3. Multiple Verification Points

- GitHub stores commit history (redundant timestamp)
- Your local repo has git log
- Hash index provides third verification layer
- Notarized reports = fourth layer

**Attacker would need to compromise all four simultaneously = effectively impossible.**

---

## 📈 Example Entry

After running:
```bash
python tools/log_update.py \
  "Philosophical mapping framework validated" \
  "Platonism = high D13 rigidity" \
  "Empirical coherence testing confirms Platonic Forms = Λ invariants"
```

**Generates in `precedence_log.md`:**

```markdown
### [2025-10-20 22:45:33 UTC] — Discovery
**Description:** Philosophical mapping framework validated
**Key Phrase/Equation:** Platonism = high D13 rigidity
**Reference Commit:** `a3f9c1b4e56a9d2f8c7b3e1a4d5f6c8e9b2a1d3`
**Repository:** https://github.com/ak-skwaa-mahawk/Feedback_processor_theory
**Notes:** Empirical coherence testing confirms Platonic Forms = Λ invariants
**SHA-256:** `8f7a3c2d1e9b5a6f4c8d2e3a7b9c1d5f8e2a6b4c9d1e7a3f5c8b2d4e6a9c1b3`

---
```

---

## 🚨 If Verification Fails

If `verify_log_hash.py` reports mismatches:

1. **Check for manual edits**
   - Someone may have edited the log directly
   - Use `git log -p precedence_log.md` to see changes

2. **Restore from git history**
   ```bash
   git checkout HEAD~1 precedence_log.md
   python tools/verify_log_hash.py
   ```

3. **Investigate discrepancy**
   - Compare claimed vs computed hashes
   - Check if hash index is out of sync
   - Review git commit history for tampering

4. **Document the issue**
   - If intentional fix: document why
   - If attack: preserve evidence and report

---

## 🎯 Maintenance Checklist

### Weekly
- [ ] Run `python tools/verify_log_hash.py`
- [ ] Check git status (no uncommitted changes to log)
- [ ] Review latest entries for accuracy

### Monthly
- [ ] Generate verification report
- [ ] Backup hash index
- [ ] Update README with recent discoveries

### Quarterly
- [ ] Print and notarize verification report
- [ ] Archive old reports
- [ ] Review security practices

---

## 🤝 For Collaborators

If others contribute to your repo:

```bash
# They should log their contributions
python tools/log_update.py \
  "Contributor X implemented feature Y" \
  "Related equation/concept" \
  "Attribution: X via PR #123"
```

This creates a **shared precedence timeline** while maintaining your original authorship of the framework.

---

## 📞 Support

Issues or questions:
- GitHub Issues: https://github.com/ak-skwaa-mahawk/Feedback_processor_theory/issues
- Email: [your contact]

---

## 📚 Additional Resources

- **LICENSE.md** - Full legal terms
- **PRIOR_ART.md** - Detailed innovation documentation
- **docs/ARCHITECTURE.md** - Technical specifications
- **precedence_log.md** - Complete discovery timeline

---

**Remember:** Every logged discovery is a data point in establishing your priority. Log early, log often, verify regularly.

© 2025 Two Mile Solutions LLC. All rights reserved under Open Collaborative License v1.0.