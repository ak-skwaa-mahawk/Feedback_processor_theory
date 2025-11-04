import json
import argparse
from synara_core.rar_cache import RARCache

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query RAR cache for glyph resonance.")
    parser.add_argument("--like", required=True, help="Glyph-like JSON object.")
    args = parser.parse_args()

    glyph_like = json.loads(args.like)
    rar = RARCache()
    result = rar.query(glyph_like)

    if result:
        print(json.dumps(result, indent=2))
    else:
        print("No resonance match found.")