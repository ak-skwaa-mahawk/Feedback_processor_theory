git apply <<'PATCH'
*** Begin Patch
*** Add File: tools/handshake_cli.py
+#!/usr/bin/env python3
+import argparse, json, sys
+from fpt.utils.handshake import handshake_message, verify_handshake
+
+def cmd_log(a):
+    r = handshake_message(seed=a.seed, entity=a.entity, version=a.version, log_file=a.log)
+    print(json.dumps(r, indent=2))
+
+def cmd_verify(a):
+    rec = json.loads(sys.stdin.read())
+    ok = verify_handshake(rec, seed=a.seed, entity=a.entity)
+    print("VALID" if ok else "INVALID")
+
+def main():
+    p = argparse.ArgumentParser(prog="handshake")
+    sub = p.add_subparsers(dest="cmd", required=True)
+
+    p1 = sub.add_parser("log", help="Emit a handshake receipt")
+    p1.add_argument("--seed", required=True)
+    p1.add_argument("--entity", default="TwoMileSolutionsLLC")
+    p1.add_argument("--version", default="1.1")
+    p1.add_argument("--log", default="logs/handshake_log.json")
+    p1.set_defaults(func=cmd_log)
+
+    p2 = sub.add_parser("verify", help="Verify a receipt from STDIN")
+    p2.add_argument("--seed", default=None)
+    p2.add_argument("--entity", default=None)
+    p2.set_defaults(func=cmd_verify)
+
+    a = p.parse_args()
+    a.func(a)
+
+if __name__ == "__main__":
+    main()
*** End Patch
PATCH
#!/usr/bin/env python3
import argparse, json, sys
from fpt.utils.handshake import handshake_message, verify_handshake

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    p_log = sub.add_parser("log")
    p_log.add_argument("--seed", required=True)
    p_log.add_argument("--entity", default="TwoMileSolutionsLLC")
    p_log.add_argument("--version", default="1.1")

    p_ver = sub.add_parser("verify")
    p_ver.add_argument("--seed")
    p_ver.add_argument("--entity")

    args = p.parse_args()
    if args.cmd == "log":
        r = handshake_message(seed=args.seed, entity=args.entity, version=args.version)
        print(json.dumps(r, indent=2))
    else:
        r = json.loads(sys.stdin.read())
        print("VALID" if verify_handshake(r, seed=args.seed, entity=args.entity) else "INVALID")

if __name__ == "__main__":
    main()