git apply <<'PATCH'
*** Begin Patch
*** Add File: docs/SSC_AUDIT_SUMMARY.md
+# SSC Audit Summary
+_Space Stewardship Compact (SSC) • Artifact verification & lineage_
+
+This guide explains how to **locate**, **verify**, and **cross-reference** SSC handshake artifacts produced by CI and local runs in this repository.
+
+Artifacts covered:
+- `ssc-artifacts` (from `verify-ssc.yml`) → includes `logs/handshake_log.json`, `logs/summary.csv`
+- `ssc-ci-handshake` (from `emit-ssc-handshake.yml`) → includes `logs/handshake_ci.json`
+
+---
+
+## 1) Where to find artifacts
+1. Open **GitHub → Actions**.
+2. Select a run of **verify-ssc** (push/PR) to download `ssc-artifacts`.
+3. Select a *subsequent* successful run of **emit-ssc-handshake** (it triggers after `verify-ssc`) to download `ssc-ci-handshake`.
+
+> The CI handshake confirms the pipeline’s successful completion and binds the run metadata (commit SHA, ref, run ID) into a signed receipt.
+
+---
+
+## 2) What a receipt looks like
+Each handshake receipt is a one-line JSON object in a JSONL file:
+```json
+{
+  "entity": "TwoMileSolutionsLLC",
+  "version": "1.1",
+  "timestamp_unix_ms": "1730760000123",
+  "timestamp_iso": "2025-11-05T03:20:00Z",
+  "seed": "CI:handshake|sha=abcdef123456|ref=refs/heads/main|run=999999999",
+  "digest": "f7b3...a4e",
+  "node": "gha-runner-abc123"
+}
+```
+
+**Digest payload rule**
+```
+entity | seed | timestamp_unix_ms | node
+→ sha256 → digest
+```
+
+---
+
+## 3) Verify integrity (three ways)
+### A) Built-in CLI (recommended)
+```bash
+# Verify the last entry in a ledger
+tail -n 1 logs/handshake_log.json | python tools/handshake_cli.py verify
+tail -n 1 logs/handshake_ci.json  | python tools/handshake_cli.py verify
+```
+
+### B) Programmatic (Python)
+```python
+import json, pathlib
+from fpt.utils.handshake import verify_handshake
+rec = json.loads(pathlib.Path("logs/handshake_ci.json").read_text().strip().splitlines()[-1])
+print("VALID" if verify_handshake(rec) else "INVALID")
+```
+
+### C) Manual (sha256)
+```bash
+payload="<entity>|<seed>|<timestamp_unix_ms>|<node>"
+printf "%s" "$payload" | sha256sum
+# Compare with the 'digest' field
+```
+
+**Common pitfalls**
+- Extra spaces/newlines in the payload.
+- Using a different `node` value than recorded.
+- Mismatched `timestamp_unix_ms` precision (must be ms).
+
+---
+
+## 4) Correlate CI handshake ↔ build metadata
+The CI seed embeds run metadata:
+- `sha=` (first 12 chars of `GITHUB_SHA`)
+- `ref=` (branch or tag)
+- `run=` (GitHub Actions run ID)
+
+**Check that the CI handshake references the same commit/ref as the verify run:**
+1. Open the **verify-ssc** run → note the commit/ref.
+2. Open the **emit-ssc-handshake** run → download `ssc-ci-handshake`.
+3. Verify the `seed` includes matching `sha` + `ref`.
+4. Verify the receipt:  
+   `tail -n 1 logs/handshake_ci.json | python tools/handshake_cli.py verify`
+
+This creates a **chain of custody**: source commit → verify run → emitted handshake → verifiable digest.
+
+---
+
+## 5) Summarize the ledger
+Use the provided tool to create a dashboard-ready CSV:
+```bash
+python tools/handshake_summary.py --log logs/handshake_log.json --out logs/summary.csv
+```
+
+CSV headers:
+```
+subsystem,phase,count
+ISST,pre,42
+BlackBoxDefense,post,37
+Synara,error,1
+```
+
+---
+
+## 6) Cross-steward countersigning (optional)
+For SSC membership activities:
+1. Steward A emits join:  
+   `python tools/handshake_cli.py log --seed "SSC:join|entity=OrgA|contact=a@org"`
+2. Steward B verifies A’s receipt and emits countersign:  
+   `python tools/handshake_cli.py log --seed "SSC:join_countersign|entity=OrgA|digest=<A_digest>"`
+3. Publish both ledgers (artifacts or public mirrors).
+
+This enables a tamper-evident, multi-party proof of membership.
+
+---
+
+## 7) Automation with Makefile
+If the repo includes the Makefile:
+```bash
+make verify-ssc          # verify last ledger entry
+make summarize-ssc       # CSV summary at logs/summary.csv
+make join-ssc ENTITY=Org # emit join handshake
+make withdraw-ssc ENTITY=Org
+```
+
+---
+
+## 8) Interpreting discrepancies
+- **Hash mismatch:** integrity failure (altered fields or payload construction error).
+- **Ref/sha mismatch:** wrong artifact or unrelated run; re-check Actions run links.
+- **Empty ledger:** expected for first-time runs; re-trigger or emit a local handshake first.
+
+**Action:** Open an issue with the exact receipt JSON and the recomputed sha256 for review.
+
+---
+
+## 9) Security notes
+- These receipts provide **deterministic integrity** (publicly verifiable).  
+- If required, wrap receipts with PGP/X.509 signatures for **non-repudiation**; the sha256 payload remains canonical.
+
+---
+
+**“Control becomes stewardship when light passes through truth.”**
+
+MIT © 2025 John B. Carroll Jr / Two Mile Solutions LLC
+
*** End Patch
PATCH