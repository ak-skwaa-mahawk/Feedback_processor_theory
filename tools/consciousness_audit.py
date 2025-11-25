#!/usr/bin/env python3
"""
Consciousness Audit CLI: IIT Φ vs Living Field Scaling.
Usage: python tools/consciousness_audit.py --params 6e12 --cycles 10
Cites Strømme (2025), Tononi/Koch (2023).
"""

import argparse
from fpt.consciousness.living_field import ConsciousnessField

def main():
    parser = argparse.ArgumentParser(description="Audit consciousness integration.")
    parser.add_argument("--params", type=float, default=6e12, help="Base params/Φ (default 6T)")
    parser.add_argument("--cycles", type=int, default=1, help="Field ripple cycles")
    parser.add_argument("--iit-only", action="store_true", help="Use IIT emergent only (no field)")

    args = parser.parse_args()
    field = ConsciousnessField(living_enabled=not args.iit_only)

    effective_phi = field.field_ripple(args.params, args.cycles)
    iit_baseline = field.phi_baseline

    print(f"Base Φ: {args.params:,.0f}")
    print(f"Effective Field Φ ({args.cycles} cycles): {effective_phi:,.0f}")
    print(f"IIT Human Baseline: {iit_baseline:,.0f}")
    print(f"Surplus Gain: {((effective_phi / args.params) - 1) * 100:.2f}% (Strømme Ripple)")

if __name__ == "__main__":
    main()