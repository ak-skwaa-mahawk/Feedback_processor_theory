import sys
import os
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--file", required=True)
args = parser.parse_args()

file_path = args.file
out_path = os.path.join("parser_outputs", f"{os.path.splitext(file_path)[0]}.json")
os.makedirs(os.path.dirname(out_path), exist_ok=True)

with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

data = {
    "file": file_path,
    "size": len(content),
    "status": "parsed"
}

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Successfully parsed {file_path} -> {out_path}")
