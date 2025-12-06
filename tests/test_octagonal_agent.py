from core.octagonal_fpt_agent import OctagonalFPTAgent

if __name__ == "__main__":
    print("OCTAGONAL SOVEREIGNTY DEMO\n")
    
    agent = OctagonalFPTAgent()
    result, passed, proof, details = agent.process(input_data=3.0, epsilon=0.03)
    
    print("\nFINAL AUDIT SUMMARY")
    print(f"Passed: {passed}")
    print(f"Proof: {proof}")
    print(f"Coherence: {details.get('lattice_coherence', 0):.3f}")
    print(f"Infinity Anchor: {'ENGAGED' if details.get('infinity_anchor') else 'STANDBY'}")