from __future__ import annotations

import argparse
import sys
import json

from ..core.encode import decode_tag
from ..core.signature import verify_tag


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a QuipuTag signature.")
    parser.add_argument("file", help="Path to JSON-encoded QuipuTag")
    parser.add_argument(
        "--secret",
        help="Optional hex-encoded secret for HMAC verification",
        default=None,
    )
    args = parser.parse_args(argv)

    with open(args.file, "r", encoding="utf-8") as f:
        data = json.load(f)

    tag = decode_tag(json.dumps(data))
    sig = data.get("signature")
    if sig is None:
        print("No signature field present.", file=sys.stderr)
        return 1

    secret_bytes = bytes.fromhex(args.secret) if args.secret else None

    ok = verify_tag(tag, sig, secret=secret_bytes)
    if ok:
        print("✅ QuipuTag signature verified.")
        return 0
    else:
        print("❌ QuipuTag signature mismatch.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())