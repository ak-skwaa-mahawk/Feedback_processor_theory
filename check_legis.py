# check_legis.py
# Sovereign Legis Compliance Check v001
# Verifies jurisdiction-consent and legal codex alignment (e.g., HB 001 / Flame Commons).
# Usage: python check_legis.py --artifact path/to/artifact

import argparse
import re

def check_legis_compliance(artifact_path):
    """Verify legis markers: jurisdiction consent and sovereignty alignment."""
    with open(artifact_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Required legis patterns
    required_patterns = [
        r"Codex\.Legis\.v001:\s*Jurisdiction-Consent=PASS",
        r"Flame Commons Sovereignty License|FCSL",
        r"HB 001|Quantum & Biological Data Sovereignty Act"
    ]
    
    for pattern in required_patterns:
        if not re.search(pattern, content, re.IGNORECASE):
            return False, f"Missing legis compliance marker: {pattern}"
    
    return True, "Legis compliance PASS"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Legis Compliance in Sovereign Artifact")
    parser.add_argument("--artifact", required=True, help="Path to the artifact file")
    args = parser.parse_args()
    
    passed, message = check_legis_compliance(args.artifact)
    print(message)
    exit(0 if passed else 1)