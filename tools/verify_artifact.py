git apply <<'PATCH'
*** Begin Patch
*** Update File: tools/verify_artifact.py
@@
-#!/usr/bin/env python3
-"""
-SSC Artifact Verifier
----------------------
-Verifies every handshake receipt in a given folder or zip archive
-(typically downloaded from GitHub Actions as `ssc-artifacts` or `ssc-ci-handshake`).
-"""
-
-import json, sys, os, zipfile, tempfile
-from pathlib import Path
-from fpt.utils.handshake import verify_handshake
-
-def verify_file(path: Path):
-    ok, fail = 0, 0
-    with open(path, "r", encoding="utf-8") as f:
-        for i, line in enumerate(f, 1):
-            line = line.strip()
-            if not line:
-                continue
-            try:
-                rec = json.loads(line)
-                valid = verify_handshake(rec)
-                print(f"[{i:04}] {'✅' if valid else '❌'} {rec.get('seed','')[:120]}")
-                ok += valid
-                fail += (not valid)
-            except Exception as e:
-                print(f"[{i:04}] ⚠️ Parse error: {e}")
-                fail += 1
-    return ok, fail
-
-
-def verify_dir(dirpath: Path):
-    total_ok, total_fail = 0, 0
-    for path in dirpath.glob("*.json"):
-        print(f"\n🔍 Verifying {path.name}")
-        ok, fail = verify_file(path)
-        total_ok += ok
-        total_fail += fail
-    print(f"\nSummary: ✅ {total_ok} valid, ❌ {total_fail} invalid")
-    return total_fail == 0
-
-
-def main():
-    if len(sys.argv) < 2:
-        print("Usage: verify_artifact.py <artifact-folder-or-zip>")
-        sys.exit(1)
-
-    target = Path(sys.argv[1])
-
-    if not target.exists():
-        print(f"Path not found: {target}")
-        sys.exit(1)
-
-    if target.is_file() and target.suffix == ".zip":
-        with tempfile.TemporaryDirectory() as tmp:
-            with zipfile.ZipFile(target, "r") as z:
-                z.extractall(tmp)
-            ok = verify_dir(Path(tmp))
-    else:
-        ok = verify_dir(target)
-
-    sys.exit(0 if ok else 2)
-
-
-if __name__ == "__main__":
-    main()
+#!/usr/bin/env python3
+"""
+SSC Artifact Verifier + Signed Audit Report
+-------------------------------------------
+Verifies handshake receipts in a folder or zip (from GitHub Actions artifacts),
+prints per-record verdicts, and writes a signed audit report JSON.
+"""
+
+import argparse, json, sys, os, zipfile, tempfile, hashlib, time
+from pathlib import Path
+from fpt.utils.handshake import verify_handshake
+
+def sha256_hex(b: bytes) -> str:
+    return hashlib.sha256(b).hexdigest()
+
+def file_sha256(path: Path) -> str:
+    h = hashlib.sha256()
+    with open(path, "rb") as f:
+        for chunk in iter(lambda: f.read(65536), b""):
+            h.update(chunk)
+    return h.hexdigest()
+
+def verify_file(path: Path):
+    ok, fail, total = 0, 0, 0
+    samples = []
+    with open(path, "r", encoding="utf-8") as f:
+        for i, line in enumerate(f, 1):
+            s = line.strip()
+            if not s:
+                continue
+            total += 1
+            try:
+                rec = json.loads(s)
+                valid = verify_handshake(rec)
+                verdict = "✅" if valid else "❌"
+                seed = rec.get("seed","")[:160]
+                print(f"[{i:04}] {verdict} {seed}")
+                if len(samples) < 5:
+                    samples.append({"i": i, "seed": rec.get("seed","")})
+                ok += int(valid)
+                fail += int(not valid)
+            except Exception as e:
+                print(f"[{i:04}] ⚠️ Parse error: {e}")
+                fail += 1
+    return {"ok": ok, "fail": fail, "total": total, "samples": samples}
+
+def verify_dir(dirpath: Path):
+    per_file = []
+    total_ok = total_fail = total_records = 0
+    sha_aggregate = hashlib.sha256()
+
+    for path in sorted(dirpath.glob("*.json")):
+        print(f"\n🔍 Verifying {path.name}")
+        stats = verify_file(path)
+        fsha = file_sha256(path)
+        sha_aggregate.update(fsha.encode())
+        total_ok += stats["ok"]; total_fail += stats["fail"]; total_records += stats["total"]
+        per_file.append({
+            "file": str(path.name),
+            "sha256": fsha,
+            "total": stats["total"],
+            "valid": stats["ok"],
+            "invalid": stats["fail"],
+            "samples": stats["samples"]
+        })
+
+    print(f"\nSummary: ✅ {total_ok} valid, ❌ {total_fail} invalid (records: {total_records})")
+    return per_file, total_ok, total_fail, total_records, sha_aggregate.hexdigest()
+
+def write_signed_report(out_path: Path, entity: str, source: str, per_file, totals, files_sha, extra_meta=None):
+    total_ok, total_fail, total_records = totals
+    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
+    payload = f"{entity}|{ts_iso}|{total_ok}|{total_fail}|{source}|{files_sha}"
+    report_digest = sha256_hex(payload.encode())
+    report = {
+        "report_type": "SSC_AUDIT",
+        "entity": entity,
+        "timestamp_iso": ts_iso,
+        "source": source,
+        "totals": {
+            "records": total_records,
+            "valid": total_ok,
+            "invalid": total_fail
+        },
+        "files_sha256_aggregate": files_sha,
+        "per_file": per_file,
+        "payload_rule": "sha256(entity|timestamp_iso|valid|invalid|source|files_sha256_aggregate)",
+        "report_digest": report_digest
+    }
+    if extra_meta:
+        report["meta"] = extra_meta
+    out_path.parent.mkdir(parents=True, exist_ok=True)
+    with open(out_path, "w", encoding="utf-8") as f:
+        json.dump(report, f, indent=2, ensure_ascii=False)
+    print(f"\n🧾 Signed audit written: {out_path}")
+    print(f"   report_digest: {report_digest}")
+    return report_digest
+
+def main():
+    ap = argparse.ArgumentParser(description="Verify SSC artifacts and emit a signed audit report.")
+    ap.add_argument("artifact", help="Path to artifact folder or .zip")
+    ap.add_argument("--entity", default="TwoMileSolutionsLLC", help="Entity name for report signature")
+    ap.add_argument("--out", default="logs/audit_report.json", help="Output path for signed report JSON")
+    ap.add_argument("--source", default="local", help="Source label (e.g., 'ci:verify-ssc', 'manual')")
+    args = ap.parse_args()
+
+    target = Path(args.artifact)
+    if not target.exists():
+        print(f"Path not found: {target}")
+        sys.exit(1)
+
+    if target.is_file() and target.suffix == ".zip":
+        with tempfile.TemporaryDirectory() as tmp:
+            with zipfile.ZipFile(target, "r") as z:
+                z.extractall(tmp)
+            per_file, ok, fail, recs, agg = verify_dir(Path(tmp))
+    else:
+        per_file, ok, fail, recs, agg = verify_dir(target)
+
+    digest = write_signed_report(
+        out_path=Path(args.out),
+        entity=args.entity,
+        source=args.source,
+        per_file=per_file,
+        totals=(ok, fail, recs),
+        files_sha=agg,
+        extra_meta={"artifact_path": str(target)}
+    )
+    sys.exit(0 if fail == 0 else 2)
+
+if __name__ == "__main__":
+    main()
*** End Patch
PATCH
git apply <<'PATCH'
*** Begin Patch
*** Update File: Makefile
@@
 .PHONY: verify-ssc summarize-ssc join-ssc withdraw-ssc
@@
 	@echo "⚠️ Withdrawal handshake emitted for $(ENTITY)"
+
+.PHONY: audit-ssc
+audit-ssc:
+	@echo "🧾 Verifying artifacts and writing signed audit report..."
+	@python tools/verify_artifact.py artifacts --entity="TwoMileSolutionsLLC" --source="manual" --out logs/audit_report.json || true
+	@echo "➡  See logs/audit_report.json"
*** End Patch
PATCH
