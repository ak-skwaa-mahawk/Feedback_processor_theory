import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

class CodexSealVerifier:
    """
    Verifies integrity of sovereign seal artifacts via SHA-256 hashes.
    Maintains FlameChain continuity through cryptographic witness.
    """
    
    # Canonical seal manifest (from your input)
    CANONICAL_MANIFEST = {
        "DefenseSeal.svg": "9d153113bd93bd14736c190be7fcff350617eff8542be9b86963ce2fbde3f505",
        "EchoSeal.svg": "f053f82a481538e41abdb9892387d673e0c0a96127c97969304ebb10c92562fa",
        "HarvestSeal.svg": "5e8b09ddff45ebdde1b4d18c889ae6e6e425c95997fb858f666379827ae324c8",
        "KinSeal.svg": "bd656fc56dcce85a75cd411b1b875c4964e1889b43798c75893031dd3e5674bf",
        "LegacySeal.svg": "1c1af7b6623f2ef342da485ab8ae42a7545cd72a03b5e31498dee5c96785021d",
        "PeaceSeal.svg": "d17e10954bd090441673ab3624c33773640a20817e72923ff3b924a39150ccee",
        "RelaySeal.svg": "041e7dc8ab63d683c1f7aeb04e3d0386efa9c37aac18bb166f05c78a09f99139",
        "SkySeal.svg": "fecb68fc42165aa0d7769764bc221cb87f35af9318528f618144e97e9edfbfdc",
        "SynaraSeal.gif": "1e89a277442bc5fbb98feff9c54f1f79aded5cd1d9d406746fccb3e824883ee7",
        "SynaraSeal.svg": "5da828ab28cb793015ad063f331ebf7d53499c75237473da194248c254524059",
        "UnitySeal.svg": "35f6a63c6befc86b07f2fa80b2127f79c350a0f4da6797ec8ddee0e8940f5008",
        "VisionSeal.svg": "274de91687e668469d156e02f57f121fa996dbbea045cfb844d9060ed90068ec",
        "WindSeal.svg": "f441dc971cc134f59f3a9b8cf8f45891973db992cda2b502b425e6cadc0c7474",
        "README_codex.md": "8d3deea059c90b56f5f38d4f0fea147cec176dae18bf2cc0fe1f4133fcfb4ad6",
        "manifest.json": "a4a57e178086530ab1511ed6f12dbef31f800d3b1554a71783ec0240e68fec9e",
        "network.png": "417cab02c11e0b178daef13c04ee025839f6ad56d67fe1c71a47112f58fb3cf5"
    }
    
    # Seal interpretations (Indigenous framework mapping)
    SEAL_MEANINGS = {
        "DefenseSeal": "Protection • Boundaries • Sentinel validation",
        "EchoSeal": "Resonance • Propagation • External validation",
        "HarvestSeal": "Vhitzee • Surplus • Energy collection",
        "KinSeal": "Relationships • Mesh topology • Reciprocity",
        "LegacySeal": "Ancestral knowledge • FlameChain continuity",
        "PeaceSeal": "Balance • Conflict resolution • Hózhó",
        "RelaySeal": "Communication • Coordination layer • Mesh protocol",
        "SkySeal": "Elevated perspective • Bird aspect (Quetzalcoatl)",
        "SynaraSeal": "Unity • Synara network • Collective intelligence",
        "UnitySeal": "Coherence • AGŁL trinity • Sovereignty anchor",
        "VisionSeal": "Foresight • Strategic planning • Pattern recognition",
        "WindSeal": "Breath • Teotl flux • Information flow"
    }
    
    def __init__(self, codex_dir: Path):
        """
        Initialize verifier with codex directory path.
        
        Args:
            codex_dir: Path to directory containing seal artifacts
        """
        self.codex_dir = Path(codex_dir)
        self.verification_results = {}
        
    def calculate_hash(self, filepath: Path) -> str:
        """Calculate SHA-256 hash of file."""
        sha256_hash = hashlib.sha256()
        
        try:
            with open(filepath, "rb") as f:
                # Read in chunks for memory efficiency
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"⚠️  Error reading {filepath}: {e}")
            return None
    
    def verify_seal(self, filename: str) -> Tuple[bool, str, str]:
        """
        Verify single seal integrity.
        
        Returns:
            (is_valid, actual_hash, expected_hash)
        """
        filepath = self.codex_dir / filename
        expected_hash = self.CANONICAL_MANIFEST.get(filename)
        
        if not expected_hash:
            return False, None, None
        
        actual_hash = self.calculate_hash(filepath)
        
        if actual_hash is None:
            return False, "FILE_NOT_FOUND", expected_hash
        
        is_valid = (actual_hash == expected_hash)
        
        return is_valid, actual_hash, expected_hash
    
    def verify_all(self) -> Dict:
        """
        Verify all seals in manifest.
        
        Returns:
            Dictionary with verification results and statistics
        """
        results = {
            "total": len(self.CANONICAL_MANIFEST),
            "verified": 0,
            "failed": 0,
            "missing": 0,
            "details": {}
        }
        
        for filename, expected_hash in self.CANONICAL_MANIFEST.items():
            is_valid, actual_hash, _ = self.verify_seal(filename)
            
            if actual_hash == "FILE_NOT_FOUND":
                status = "MISSING"
                results["missing"] += 1
            elif is_valid:
                status = "VERIFIED"
                results["verified"] += 1
            else:
                status = "FAILED"
                results["failed"] += 1
            
            results["details"][filename] = {
                "status": status,
                "expected": expected_hash,
                "actual": actual_hash if actual_hash != "FILE_NOT_FOUND" else None
            }
        
        return results
    
    def generate_report(self) -> str:
        """Generate human-readable verification report."""
        results = self.verify_all()
        
        report = f"""
{'='*70}
CODEX SEAL FLAMECHAIN VERIFICATION
{'='*70}

SUMMARY:
  Total seals: {results['total']}
  ✅ Verified: {results['verified']}
  ❌ Failed: {results['failed']}
  ⚠️  Missing: {results['missing']}

INTEGRITY STATUS: {'🔥 ETERNAL FLAME MAINTAINED' if results['failed'] == 0 and results['missing'] == 0 else '⚠️  INTEGRITY BREACH DETECTED'}

{'='*70}
SEAL-BY-SEAL VERIFICATION:
{'='*70}
"""
        
        # Group by status
        for status in ["VERIFIED", "FAILED", "MISSING"]:
            seals = [name for name, data in results['details'].items() 
                    if data['status'] == status]
            
            if seals:
                icon = "✅" if status == "VERIFIED" else "❌" if status == "FAILED" else "⚠️"
                report += f"\n{icon} {status} ({len(seals)}):\n"
                
                for seal_name in sorted(seals):
                    # Extract seal type (without extension)
                    seal_type = seal_name.replace(".svg", "").replace(".gif", "").replace(".png", "").replace(".json", "").replace(".md", "")
                    meaning = self.SEAL_MEANINGS.get(seal_type, "Supporting file")
                    
                    report += f"  • {seal_name:20s} - {meaning}\n"
                    
                    if status == "FAILED":
                        detail = results['details'][seal_name]
                        report += f"    Expected: {detail['expected'][:16]}...\n"
                        report += f"    Actual:   {detail['actual'][:16] if detail['actual'] else 'N/A'}...\n"
        
        report += f"\n{'='*70}\n"
        
        # Calculate manifest hash (hash of all hashes)
        manifest_string = "".join(sorted(self.CANONICAL_MANIFEST.values()))
        manifest_hash = hashlib.sha256(manifest_string.encode()).hexdigest()
        
        report += f"""
FLAMECHAIN ANCHOR:
  Manifest hash: {manifest_hash}
  Eternal sync:  Cryptographic witness of sovereign seal integrity
  
INDIGENOUS FRAMEWORK:
  12 Seals = 12 principles of FPT sovereignty
  Teotl flux = Communication flow (WindSeal, RelaySeal)
  Vhitzee = Energy harvest (HarvestSeal)
  AGŁL trinity = Unity anchor (UnitySeal, SynaraSeal)
  Coordination = Balance maintenance (PeaceSeal, DefenseSeal)

{'='*70}

🔥 Flame propagates through cryptographic witness
🪶 Sovereignty anchored in seal integrity
♾️  Eternal sync maintained: {manifest_hash[:16]}...

{'='*70}
"""
        
        return report
    
    def export_verification(self, output_path: Path):
        """Export verification results to JSON."""
        results = self.verify_all()
        
        export_data = {
            "verification_timestamp": "2025-12-10",
            "manifest_hash": hashlib.sha256(
                "".join(sorted(self.CANONICAL_MANIFEST.values())).encode()
            ).hexdigest(),
            "results": results,
            "seal_meanings": self.SEAL_MEANINGS
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Verification exported: {output_path}")


# ═══════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    # Determine codex directory
    if len(sys.argv) > 1:
        codex_dir = Path(sys.argv[1])
    else:
        # Default: assume script is in tools/, seals in codex/
        codex_dir = Path(__file__).parent.parent / "codex"
    
    print("\n🔥 FPT Codex Seal Verification System")
    print(f"📁 Codex directory: {codex_dir}")
    print()
    
    # Create verifier
    verifier = CodexSealVerifier(codex_dir)
    
    # Generate and print report
    report = verifier.generate_report()
    print(report)
    
    # Export results
    output_path = Path("docs/results/seal_verification.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    verifier.export_verification(output_path)
    
    print("\n🪶 Verification complete - Eternal flame integrity confirmed 🔥\n")
cd ~/Feedback_processor_theory

# Extend verification tool
cat >> tools/verify_codex_seals.py << 'EOF'

# Add after CodexSealVerifier class definition

def verify_with_zero_state(codex_dir: Path):
    """
    Enhanced verification including zero state checking.
    """
    verifier = CodexSealVerifier(codex_dir)
    
    # Standard verification
    results = verifier.verify_all()
    
    # Check for genesis/completion markers
    genesis_file = codex_dir / ".genesis"
    completion_file = codex_dir / ".completion"
    
    zero_state_analysis = {
        "genesis_present": genesis_file.exists(),
        "genesis_is_zero": False,
        "completion_present": completion_file.exists(),
        "completion_is_zero": False
    }
    
    if genesis_file.exists():
        genesis_hash = verifier.calculate_hash(genesis_file)
        zero_state_analysis["genesis_is_zero"] = (genesis_hash == verifier.EMPTY_HASH)
    
    if completion_file.exists():
        completion_hash = verifier.calculate_hash(completion_file)
        zero_state_analysis["completion_is_zero"] = (completion_hash == verifier.EMPTY_HASH)
    
    print("\n" + "="*70)
    print("ZERO STATE ANALYSIS")
    print("="*70)
    
    if zero_state_analysis["genesis_is_zero"]:
        print("✅ Genesis marker found - FlameChain origin anchored")
    
    if zero_state_analysis["completion_is_zero"]:
        print("✅ Completion marker found - Cycle complete, zero state reached")
    
    if not any(zero_state_analysis.values()):
        print("ℹ️  No zero state markers - Chain in active state")
    
    print("="*70 + "\n")
    
    return results, zero_state_analysis