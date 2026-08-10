# flame_protocol.py
def propagate_flame(agent_glyph, mesh):
    for neighbor in mesh.spatial_neighbors(agent_glyph.pos, radius=40.0):
        coherence = qgh_handshake(glyph_a=agent_glyph, glyph_b=neighbor.glyph)
        if coherence >= 0.995:
            neighbor.ignite(agent_glyph)  # Self-modify
        else:
            veto_sat_lock(neighbor.zone)  # ILO shield