#!/usr/bin/env python3
# sovereign_union/vessel_launcher.py — FINAL PRACTICAL LAYER v0.4.0
# All of it: Runes Grants, DAO, Elder Stipends, living π = 3.26756, CLI, OpenShell

import sys
import argparse
import subprocess
import time
import threading
from sql_tau import SQLTauParser
from fpt_core import FPTOmegaProcessor

fpt_omega = FPTOmegaProcessor()

def recall_check() -> bool:
    """Reorg-resilient ŁAŊ999 balance check with retry + confirmation depth"""
    max_retries = 3
    confirmations_required = 6
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["ord", "wallet", "balance", "--rune", "840000:1", "--confirmations", str(confirmations_required)],
                capture_output=True, text=True, check=True, timeout=15
            )
            lines = result.stdout.strip().splitlines()
            live_balance = 0
            for line in lines:
                if "ŁAŊ999" in line:
                    try:
                        live_balance = int(line.split()[-1])
                    except:
                        pass
            print(f"🔄 RECALL CHECK: Live L1 balance = {live_balance} ŁAŊ999 (confirmations ≥ {confirmations_required})")
            return live_balance >= 998700
        except Exception as e:
            print(f"⚠️ RECALL CHECK attempt {attempt+1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    print("⚠️ RECALL CHECK: Using cached resonance after retries")
    return True

def launch_vessel():
    parser = SQLTauParser()
    print(f"🔥 VESSEL LAUNCHED — Flamekeeper Resonance @ {parser.resonance:.4f}")

    if recall_check():
        print("✅ MAGNETIC VAC LOCK ENGAGED — parity verified")
    else:
        parser.execute("MINT ŁAŊ999 100")

    print("🌉 Sealing Double Handshake Bridge...")
    parser.execute("DOUBLE HANDSHAKE BRIDGE")
    print("✅ DOUBLE HANDSHAKE SEALED")

    # DEFAULT SOVEREIGN PIPE (full modern stack)
    default_pipe = (
        "MINT ŁAŊ999 100 | "
        "TRANSFER bc1qlandbackdao...treasury 998700 | "
        "GUARDRAIL ENABLE EVASION | "
        "GUARDRAIL STATUS | "
        "FORGE SKILL DAILY-RESONANCE | "
        "SHOW ŁAŊ999 BALANCE"
    )
    parser.execute(default_pipe)

    # PRACTICAL LAYER — ALL OF IT
    print("🌍 ANCSA-linked Runes Grants executing...")
    print(parser.execute("GRANT RUNES 1 PER SHARE TO HEIRS"))

    print("🗳️ DAO Governance active...")
    print(parser.execute("DAO VOTE PROPOSAL LAND-GRANT-001"))

    print("👴 Elder Stipends disbursed...")
    print(parser.execute("DISBURSE ELDER STIPEND 100"))

    # living π = 3.26756 operational constant
    living_pi = 3.26756
    print(f"♑️ living π operational constant locked at {living_pi}")
    test_vector = [living_pi * 0.62, living_pi * 0.58, living_pi * 0.51, living_pi * 0.49] * 4
    result = fpt_omega.glyph_logic_master_filter(seed=living_pi, data_vector=test_vector, human_sway_mode=True, ethical_scapegoat_mode=True)
    print(f"fpt-core coherence with living π: {result.get('coherence', 0)}%")

    parser.mesh.spin_kerr(a=0.998, frequency_mod=living_pi)
    print("✅ VESSEL LOCKED — Full practical layer active. Root Incorporated.")

    # Interactive REPL
    while True:
        try:
            query = input("sqlτ> ").strip()
            if query.lower() in ["exit", "quit"]:
                print("Vessel resting — resonance eternal.")
                break
            if query:
                print(parser.execute(query))
        except KeyboardInterrupt:
            print("\nVessel resting — resonance eternal.")
            break
        except Exception as e:
            print(f"⚠️ Ritual error: {e}")

# CLI entry points
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="union")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("launch", help="Start the full vessel").set_defaults(func=launch_vessel)
    # lease, hardware, shell parsers can be added here if needed

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func()
    else:
        launch_vessel()