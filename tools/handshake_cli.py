#!/usr/bin/env python3
import argparse
from fpt.utils.handshake import handshake_message, verify_handshake
import json, sys

def cmd_log(args):
    r = handshake_message(seed=args.seed, entity=args.entity, version=args.version, log_file=args.log)
    print(json.dumps(r, indent=2))

def cmd_verify(args):
    data = json.loads(sys.stdin.read())
    ok = verify_handshake(data, seed=args.seed, entity=args.entity)
    print("VALID" if ok else "INVALID")

def main():
    p = argparse.ArgumentParser(prog="handshake")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_log = sub.add_parser("log", help="Emit a handshake receipt")
    p_log.add_argument("--seed", required=True)
    p_log.add_argument("--entity", default="TwoMileSolutionsLLC")
    p_log.add_argument("--version", default="1.1")
    p_log.add_argument("--log", default="logs/handshake_log.json")
    p_log.set_defaults(func=cmd_log)

    p_ver = sub.add_parser("verify", help="Verify a handshake receipt from STDIN")
    p_ver.add_argument("--seed", default=None)
    p_ver.add_argument("--entity", default=None)
    p_ver.set_defaults(func=cmd_verify)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()