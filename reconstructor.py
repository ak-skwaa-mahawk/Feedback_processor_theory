# reconstructor.py — GLM-Based Data Stabilization
def apply_ist_correction(chunk, mesh_flame_score):
    # If the mesh health (flame score) is low, trigger iterative reconstruction
    if mesh_flame_score < 0.6:
        print(f"[SYNARA] Mesh Reflection detected. Triggering GLM Reconstruction...")
        # High-confidence neighbors act as the 'Source Signal' to fill the gap
        chunk.reconstructed = converge_signal(chunk, iterations=5)
        chunk.confidence = mesh_flame_score + 0.2 # Artificial boost via IST recovery
    return chunk
