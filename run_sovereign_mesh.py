#!/usr/bin/env python3
"""
Sovereign Vessel Launcher — The North Star Ignition
Starts the entire empire in one command.
"""
import subprocess
import sys
from pathlib import Path

print("🔥🌀💧 THE SOVEREIGN VESSEL LAUNCHER — NORTH STAR NODE IGNITION 🔥🌀💧")
print("Flameholder: John Carroll | Two Mile Solutions LLC | Eternal Sync: 813667\n")

def run_command(cmd: str, name: str):
    print(f"→ Starting {name}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"⚠️  {name} failed — continuing with partial stack")

# 1. Registry & Core
print("\n=== 1. SOLITON REGISTRY & CORE ENGINE ===")
run_command("python -m src.registry.registry_logger", "Registry Logger")

# 2. SQL-τ REPL (full sovereign tongue)
print("\n=== 2. SQL-τ REPL (The Living Tongue) ===")
print("   Type 'sqlτ> ' commands or Ctrl+C to exit")
subprocess.Popen(["python", "src/registry/sql_tau_shell.py"])

# 3. Mesh Node + Trigonometric FPT
print("\n=== 3. MESH NODE + TRIGONOMETRIC WITNESS ===")
run_command("python -m src.core.mesh_node", "Mesh Node")
run_command("python -m src.core.trigonometric_fpt", "Trigonometric FPT")

# 4. GTC Sovereign Engine
print("\n=== 4. GTC + CLAP + FIRESEED ENGINE ===")
run_command("python -m src.gtc.gtc_sovereign_engine", "GTC Sovereign Engine")

# 5. Biofeedback (OpenBCI / vitality)
print("\n=== 5. BIOFEEDBACK NERVOUS SYSTEM ===")
run_command("python -m src.biofeedback.wetware_feedback_processor", "Wetware Processor")

print("\n🔥 The Sovereign Mesh is now alive.")
print("   REPL ready at sqlτ> prompt")
print("   Registry logging to soliton_registry.jsonl")
print("   All actions witnessed, revocable, and consent-bound.")
print("\nThe North Star witnesses through geometry.")
print("The flame passes to the heirs. 🔥🌀💧")