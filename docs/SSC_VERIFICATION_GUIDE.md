---
## Appendix — CLI Automation via Makefile

For ease of use, the repository provides a set of Makefile commands that wrap the verification utilities.

### 🔧 Quick Commands

| Command | Description |
|----------|--------------|
| `make verify-ssc` | Verifies the most recent handshake in `logs/handshake_log.json` |
| `make summarize-ssc` | Produces a CSV summary (`logs/summary.csv`) of all handshake events |
| `make join-ssc ENTITY="YourOrg"` | Emits an SSC join handshake for your entity |
| `make withdraw-ssc ENTITY="YourOrg"` | Emits an SSC withdrawal handshake |

### 📘 Examples

**Verify last receipt**
```bash
make verify-ssc
git apply <<'PATCH'
*** Begin Patch
*** Add File: docs/SSC_VERIFICATION_GUIDE.md
+# SSC Verification Guide
+_Space Stewardship Compact (SSC) • Two Mile Solutions LLC_
+
+This guide explains how a new steward can **generate**, **publish**, and **verify** Space Stewardship Compact join handshakes using the Feedback Processor Theory (FPT) utilities.
+
+---
+
+## 0) Prerequisites
+- **Python 3.10+**
+- Repo cloned locally (this project)
+- The handshake utilities present:
+  - `fpt/utils/handshake.py`
+  - `tools/handshake_cli.py`
+  - (optional) `tools/handshake_summary.py`
+
+> If these files aren’t present, pull the latest main branch or add them from the README instructions.
+
+---
+
+## 1) Create a Join Handshake
+Your **join** event must emit a signed receipt that can be verified by others.
+
+**CLI (recommended)**
+```bash
+python tools/handshake_cli.py log --seed "SSC:join|entity=<YourOrg>|contact=<email>"
+```
+
+**Programmatic**
+```python
+from fpt.utils.handshake import handshake_message
+receipt = handshake_message("SSC:join|entity=<YourOrg>|contact=<email>")
+print(receipt)
+```
+
+This writes a JSON object to `logs/handshake_log.json` (JSONL format, one receipt per line).
+
+**Receipt fields**
+| key | meaning |
+|---|---|
+| `entity` | Sovereign root (default: `TwoMileSolutionsLLC`; may be customized if you fork) |
+| `version` | Handshake protocol version |
+| `timestamp_unix_ms` | Millisecond epoch (UTC) |
+| `timestamp_iso` | ISO-8601 UTC timestamp |
+| `seed` | Descriptive string of the event (e.g., `SSC:join|entity=YourOrg`) |
+| `digest` | SHA-256 of `entity|seed|timestamp_unix_ms|node` |
+| `node` | Hostname that emitted the handshake |
+
+---
+
+## 2) Publish Your Ledger
+Compact stewards must provide an auditable ledger.
+
+- **Default location:** `logs/handshake_log.json` (JSONL)
+- **Options to publish:**
+  1. Commit and push the log (if you’re comfortable with public visibility).
+  2. Publish as a GitHub Actions **artifact** (recommended).
+  3. Mirror to an immutable bucket or registry you control.
+
+**Recommended CI (artifact)**
+Add a workflow (example provided in project README as `.github/workflows/handshake.yml`) that:
+1. Emits a CI handshake: `CI:handshake|sha=<commit>|ref=<branch>`
+2. Uploads `logs/*.json` as an artifact named `handshake-logs`
+
+This creates a verifiable trail for each push without committing logs to the repo.
+
+---
+
+## 3) Verify a Receipt (Self-check)
+You (and peers) should be able to re-verify any handshake.
+
+**CLI verification (STDIN)**
+```bash
+# Example: verify the last line in your local ledger
+tail -n 1 logs/handshake_log.json | python tools/handshake_cli.py verify
+```
+Expected output:
+```
+VALID
+```
+
+**Programmatic verification**
+```python
+import json, pathlib
+from fpt.utils.handshake import verify_handshake
+
+path = pathlib.Path("logs/handshake_log.json")
+rec = json.loads(path.read_text().strip().splitlines()[-1])
+print("VALID" if verify_handshake(rec) else "INVALID")
+```
+
+**Manual digest recompute (advanced)**
+1. Build the payload string exactly:
+   ```
+   <entity>|<seed>|<timestamp_unix_ms>|<node>
+   ```
+2. Compute SHA-256:
+   ```bash
+   # Linux/macOS
+   printf "%s" "<payload>" | shasum -a 256
+   # or
+   printf "%s" "<payload>" | sha256sum
+   ```
+3. Compare to the `digest` field. If they match, integrity is confirmed.
+
+> **Gotchas:**  
+> - Don’t add extra whitespace or newlines to the payload.  
+> - Use the exact `timestamp_unix_ms` and `node` values from the receipt.  
+> - The `seed` must match character-for-character (including `|k=v` segments).
+
+---
+
+## 4) Cross-Steward Validation (Peer review)
+To finalize SSC membership, at least **two** existing stewards (in addition to the root) should validate your join.
+
+**Reviewer steps**
+1. Obtain the steward’s latest ledger (download artifact or retrieve `logs/handshake_log.json`).  
+2. Run:
+   ```bash
+   tail -n 1 path/to/handshake_log.json | python tools/handshake_cli.py verify
+   ```
+3. Emit a countersign handshake referencing the join digest:
+   ```bash
+   python tools/handshake_cli.py log --seed "SSC:join_countersign|entity=<YourOrg>|digest=<digest>"
+   ```
+4. (Optional) Open a PR or issue linking the proof to the public registry.
+
+---
+
+## 5) Monthly Audit Summary
+Produce a quick CSV of counts by subsystem/phase as part of routine stewardship.
+
+```bash
+python tools/handshake_summary.py --log logs/handshake_log.json --out summary.csv
+```
+
+Sample CSV headers:
+```
+subsystem,phase,count
+ISST,pre,42
+BlackBoxDefense,post,37
+Synara,error,1
+```
+
+Share this file or post a screenshot in your project’s releases for transparency.
+
+---
+
+## 6) Join / Withdraw (Event Seeds)
+**Join (you)**
+```bash
+python tools/handshake_cli.py log --seed "SSC:join|entity=<YourOrg>|contact=<email>"
+```
+**Countersign (existing steward)**
+```bash
+python tools/handshake_cli.py log --seed "SSC:join_countersign|entity=<YourOrg>|digest=<digest>"
+```
+**Withdraw**
+```bash
+python tools/handshake_cli.py log --seed "SSC:withdraw|entity=<YourOrg>"
+```
+
+All such events remain verifiable by recomputing the digest, ensuring a tamper-evident historical chain.
+
+---
+
+## 7) Troubleshooting
+**Issue:** `INVALID` during verify  
+**Check:**  
+- Payload mismatch (extra spaces, wrong delimiter, or wrong timestamp precision).  
+- Different `node` than the original (verification must use the recorded `node`).  
+- Encoding issues (ensure UTF-8; the code uses `ensure_ascii=False` for non-ASCII seeds).
+
+**Issue:** Ledger not found  
+- Ensure your workflow / local run created `logs/handshake_log.json`.  
+- Confirm that your process has write permission to `logs/`.  
+- If using CI artifacts, make sure the workflow uploaded `logs/*.json`.
+
+---
+
+## 8) Security Notes
+- The handshake is **deterministic integrity**, not a signature with a private key. It’s designed for **transparent, distributed attestation**.  
+- For higher-assurance contexts, you may wrap the handshake JSON with a PGP or X.509 signature — the base digest remains the canonical payload check.
+
+---
+
+## Appendix — Minimal API Reference
+```python
+from fpt.utils.handshake import handshake_message, verify_handshake
+from fpt.utils.hs import hs                     # optional seed wrapper
+from fpt.utils.decorators import handshake_step # optional decorator
+```
+
+- `handshake_message(seed, entity="TwoMileSolutionsLLC", version="1.1", log_file="logs/handshake_log.json") -> dict`  
+- `verify_handshake(receipt, seed=None, entity=None) -> bool`  
+- `hs(subsys, phase, **kv)` builds canonical seeds like `ISST:post|stage=glyph_to_meta|n=18`  
+- `@handshake_step("ISST","coherence_eval")` auto-emits `pre/post/error` around any function
+
+---
+
+**“Control becomes stewardship when light passes through truth.”**
+
+MIT © 2025 John B. Carroll Jr / Two Mile Solutions LLC
+
*** End Patch
PATCH