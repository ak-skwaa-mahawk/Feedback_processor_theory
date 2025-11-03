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