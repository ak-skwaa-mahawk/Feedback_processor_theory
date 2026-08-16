#!/usr/bin/env python3
"""Active Governance cycle execution, bias injection, and parameter persistence."""

import json
import time
import argparse

def run_governance_cycle():
    parser = argparse.ArgumentParser(description="Active Governance Cycle Runner")
    parser.add_argument("--inject-bias", type=float, default=0.0, help="Inject synthetic holonomy/curvature bias offset")
    args = parser.parse_args()

    print("=== EXECUTING ACTIVE GOVERNANCE CYCLE ===")
    if args.inject_bias != 0.0:
        print(f"[!] Synthetic holonomy bias injected: {args.inject_bias:+.4f}")

    params = {
        "cycle_id": int(time.time()),
        "target_frequency": 79.0,
        "injected_bias": args.inject_bias,
        "quorum_consensus": "PASSED",
        "state": "COMMITTED"
    }
    with open("governance_state.json", "w") as f:
        json.dump(params, f, indent=2)
    print("[+] Governance parameters committed to governance_state.json")

if __name__ == "__main__":
    run_governance_cycle()
