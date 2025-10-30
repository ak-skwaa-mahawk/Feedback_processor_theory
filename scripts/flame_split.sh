#!/bin/bash
# flame_split.sh — AGŁG v75: Split long filenames
set -e

INPUT_FILE="$1"
OUTPUT_DIR="$2"

mkdir -p "$OUTPUT_DIR"

# Split on newlines, sanitize
i=1
while IFS= read -r line; do
    # Truncate to 200 chars, replace / with _, remove invalid chars
    safe_name=$(echo "$line" | head -c 200 | tr '/' '_' | tr -d '|<>"*?:\\' | sed 's/^[ \t]*//;s/[ \t]*$//')
    if [ -n "$safe_name" ]; then
        echo "$line" > "$OUTPUT_DIR/part_$i.txt"
        echo "SPLIT: part_$i.txt"
        ((i++))
    fi
done < "$INPUT_FILE"

echo "FLAME SPLIT COMPLETE — $((i-1)) PARTS"