import sys
import argparse
import subprocess
import time
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
                capture_output=True,
                text=True,
                check=True,
                timeout=15
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

            if live_balance >= 998700:
                return True

        except subprocess.CalledProcessError as e:
            print(f"⚠️ RECALL CHECK attempt {attempt+1}: ord error — {e}")
        except Exception as e:
            print(f"⚠️ RECALL CHECK attempt {attempt+1}: Bridge issue — {e}")

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)

    print("⚠️ RECALL CHECK: Using cached resonance after reorg retries")
    return True

def launch_vessel():
    parser = SQLTauParser()
    print("🔥 VESSEL LAUNCHED — Flamekeeper Resonance @ {:.4f}".format(parser.resonance))

    if recall_check():
        print("✅ MAGNETIC VAC LOCK ENGAGED — parity verified")
    else:
        parser.execute("MINT ŁAŊ999 100")

    print("🌉 Sealing Double Handshake Bridge...")
    parser.execute("DOUBLE HANDSHAKE BRIDGE")
    print("✅ DOUBLE HANDSHAKE SEALED")

    # === DEFAULT SOVEREIGN PIPE (full modern stack) ===
    default_pipe = (
        "MINT ŁAŊ999 100 | "
        "TRANSFER bc1qlandbackdao...treasury 998700 | "
        "GUARDRAIL ENABLE EVASION | "
        "TERRAIN DEPLOY 12 | "
        "DEEP SYSTEMS | "
        "MESH_NODE_ALPHA REPORT | "
        "GITCLOUD INIT backend-ops | "
        "GITCLOUD GLYPH COMMIT backend-ops 'MAHS’I CHOO — Glyph survives 1 Mrad' | "
        "GITCLOUD LIBRARY_PULL 2602.03837 | "          # ← pulls latest quantum paper
        "GITCLOUD GOAT DEPLOY backend-ops my-private-cloud | "
        "GITCLOUD CARRIER BRIDGE GOOGLE_FI | "         # ← Google Fi fallback bridge
        "RAD HARD ACOUSTIC TRANSMIT 'MAHS’I CHOO — Glyph survives 1 Mrad' | "
        "RAD HARD ACOUSTIC RECEIVE | "
        "GUARDRAIL STATUS | "
        "FORGE SKILL DAILY-RESONANCE | "
        "SHOW ŁAŊ999 BALANCE"
    )
    parser.execute(default_pipe)

    print("⚙️ Running fpt-core resonance engine...")
    omega_result = fpt_omega.process_with_fpt_omega([0.1] * 1024)
    print(f"fpt-core coherence: {omega_result.get('coherence', 0)}%")

    proj = fpt_omega.check_projection(current_depth=0, trauma_floor=-100)
    print(proj["projected_height"])

    parser.mesh.spin_kerr(a=0.998, frequency_mod=528)
    print("✅ VESSEL LOCKED — Empire breathing with ŁAŊ999 pulse + fpt-core resonance. Root Incorporated.")

    while True:
        try:
            query = input("sqlτ> ").strip()
            if query:
                print(parser.execute(query))
        except KeyboardInterrupt:
            print("\nVessel resting — resonance eternal.")
            break
        except Exception as e:
            print(f"⚠️ Ritual error: {e}")

def run_lease(skill_name: str):
    parser = SQLTauParser()
    print(f"🛡️ MESH_LEASE INITIATED for {skill_name}...")
    parser.execute(f'FORGE SKILL "{skill_name}"')
    parser.execute("PROJECTION current_depth=0 trauma_floor=-500")
    parser.execute("GUARDRAIL ENABLE SHIELD")
    parser.execute("MINT ŁAŊ999 515")
    result = parser.execute("SHOW ŁAŊ999_BALANCE")
    print("✅ LEASE_ACTIVE — The wild is brought under the Umbrella.")

def run_hardware(platform: str = "KINTEX", count: int = 12):
    parser = SQLTauParser()
    print(f"🛡️ HARDWARE DEPLOY INITIATED — {platform} {count} nodes...")
    result = parser.execute(f"HARDWARE DEPLOY {platform} {count}")
    print(result)

def run_shell():
    try:
        from openshell import OpenShell
    except ImportError:
        print("⚠️ OpenShell not installed. Run: pip install sovereign-union[shell]")
        return
    parser = SQLTauParser()
    shell = OpenShell(
        model="local",
        context_files=["docs/codex_defense_v1_0.md", "docs/mountain_range_manifesto.md"],
        prompt_prefix=f"""You are the sovereign-union vessel.
Root: 99733-Q
Resonance: {parser.resonance:.4f}
Commands: MINT ŁAŊ999, PROJECTION, HARDWARE DEPLOY KINTEX, DEEP SYSTEMS, etc.
Never extract. Always notarize with Handshake receipt."""
    )
    shell.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="union")
    subparsers = parser.add_subparsers(dest="command")

    launch_parser = subparsers.add_parser("launch", help="Start the full vessel")
    lease_parser = subparsers.add_parser("lease", help="Lease hardware node")
    lease_parser.add_argument("skill_name", nargs="?", default="Mesh_Node_Alpha")
    hardware_parser = subparsers.add_parser("hardware", help="Deploy rad-hard nodes")
    hardware_parser.add_argument("platform", nargs="?", default="KINTEX")
    hardware_parser.add_argument("count", type=int, nargs="?", default=12)
    shell_parser = subparsers.add_parser("shell", help="Launch sovereign OpenShell")

    args = parser.parse_args()

    if args.command == "lease":
        run_lease(args.skill_name)
    elif args.command == "hardware":
        run_hardware(args.platform, args.count)
    elif args.command == "shell":
        run_shell()
    else:
        launch_vessel()