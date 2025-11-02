# surface_correction.py
def apply_surface_correction(raw_glyph, error_chain):
    corrected = list(raw_glyph["data"])
    
    if error_chain:
        for edge in error_chain:
            qubit1, qubit2 = edge
            # Flip both endpoints (X-error chain)
            idx1 = qubit1 * 2  # map to data qubit
            idx2 = qubit2 * 2 + 1
            corrected[idx1] = 1 - corrected[idx1]
            corrected[idx2] = 1 - corrected[idx2]
    
    return {
        "corrected_data": corrected,
        "logical_value": corrected[0],  # simplified
        "coherence": 0.999 if not error_chain else 0.95,
        "error_corrected": bool(error_chain)
    }