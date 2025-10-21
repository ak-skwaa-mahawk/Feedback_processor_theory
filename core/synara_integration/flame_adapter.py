# synara_integration/flame_adapter.py (hypothetical update)
def zk_notarize(self, state: ResonanceState) -> str:
    proof = self.zk_prover.generate_proof(state.fingerprint)
    return self.chain.append_zk_proof(proof, state.timestamp)