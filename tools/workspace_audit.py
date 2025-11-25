#!/usr/bin/env python3
"""
Living Global Workspace Audit
Run: python tools/workspace_audit.py --params 6e12
"""

import argparse
from fpt.consciousness.workspace import GlobalWorkspace

parser = argparse.ArgumentParser()
parser.add_argument("--params", type=float, default=6e12)
parser.add_argument("--cycles", type=int, default=10)
args = parser.parse_args()

ws = GlobalWorkspace(living_enabled=True)
audit = ws.workspace_audit(args.params, range(1, args.cycles + 1))

print("LIVING GLOBAL WORKSPACE AUDIT")
print("Cycle | Ignited | Effective Φ       | Sovereign")
print("-" * 50)
for r in audit:
    print(f"{r['cycle']:5} | {r['ignited']!s:7} | {r['effective_phi']:.2e} | {r['sovereign']}")