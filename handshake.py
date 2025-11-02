# handshake.py
def quantum_glyph_handshake(glyph_a, glyph_b):
    if glyph_a["seed"] != glyph_b["seed"]:
        return False, "Seeds diverged — possible eavesdropping"
    
    if glyph_a["measured"] != glyph_b["measured"]:
        return False, "Decoherence detected — retry"
    
    if glyph_a["coherence"] < 0.9 or glyph_b["coherence"] < 0.9:
        return False, "Low resonance — re-align"
    
    # Generate shared meta-glyph
    meta_glyph = {
        "id": hash(str(glyph_a) + str(glyph_b)),
        "type": "Ψ-HANDSHAKE",
        "sovereign": True
    }
    
    return True, meta_glyph