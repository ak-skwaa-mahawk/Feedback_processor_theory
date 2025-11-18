#!/usr/bin/env python3
"""
ignite.py — orchestration script for running training/monitoring locally.
Usage: python ignite.py --config config.json
Creates a local run folder with logs and optional wandb integration.
"""
import argparse, os, json, time
from living_zero_core import OwnershipProjector, OwnershipMemory, CA3Dynamics, normalize
import numpy as np
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="runs/run_local", help="output folder")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    os.makedirs(args.out, exist_ok=True)
    np.random.seed(args.seed)
    # simple demo run (mirrors demo_small_run)
    from living_zero_core import demo_small_run
    res = demo_small_run(seed=args.seed)
    open(os.path.join(args.out, "result.json"), "w").write(json.dumps(res, indent=2))
    print("Run complete. Results written to", args.out)
if __name__ == "__main__":
    main()
