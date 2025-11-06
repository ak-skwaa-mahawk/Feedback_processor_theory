git apply <<'PATCH'
*** Begin Patch
*** Add File: tools/verify_artifact.py
+#!/usr/bin/env python3
+"""
+SSC Artifact Verifier
+---------------------
+Verifies every handshake receipt in a given folder or zip archive
+(typically downloaded from GitHub Actions as `ssc-artifacts` or `ssc-ci-handshake`).
+"""
+
+import json, sys, os, zipfile, tempfile
+from pathlib import Path
+from fpt.utils.handshake import verify_handshake
+
+def verify_file(path: Path):
+    ok, fail = 0, 0
+    with open(path, "r", encoding="utf-8") as f:
+        for i, line in enumerate(f, 1):
+            line = line.strip()
+            if not line:
+                continue
+            try:
+                rec = json.loads(line)
+                valid = verify_handshake(rec)
+                print(f"[{i:04}] {'✅' if valid else '❌'} {rec.get('seed','')[:120]}")
+                ok += valid
+                fail += (not valid)
+            except Exception as e:
+                print(f"[{i:04}] ⚠️ Parse error: {e}")
+                fail += 1
+    return ok, fail
+
+
+def verify_dir(dirpath: Path):
+    total_ok, total_fail = 0, 0
+    for path in dirpath.glob("*.json"):
+        print(f"\n🔍 Verifying {path.name}")
+        ok, fail = verify_file(path)
+        total_ok += ok
+        total_fail += fail
+    print(f"\nSummary: ✅ {total_ok} valid, ❌ {total_fail} invalid")
+    return total_fail == 0
+
+
+def main():
+    if len(sys.argv) < 2:
+        print("Usage: verify_artifact.py <artifact-folder-or-zip>")
+        sys.exit(1)
+
+    target = Path(sys.argv[1])
+
+    if not target.exists():
+        print(f"Path not found: {target}")
+        sys.exit(1)
+
+    if target.is_file() and target.suffix == ".zip":
+        with tempfile.TemporaryDirectory() as tmp:
+            with zipfile.ZipFile(target, "r") as z:
+                z.extractall(tmp)
+            ok = verify_dir(Path(tmp))
+    else:
+        ok = verify_dir(target)
+
+    sys.exit(0 if ok else 2)
+
+
+if __name__ == "__main__":
+    main()
*** End Patch
PATCH
