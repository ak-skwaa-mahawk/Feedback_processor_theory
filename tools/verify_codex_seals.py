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