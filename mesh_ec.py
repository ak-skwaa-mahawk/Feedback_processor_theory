# mesh_ec.py
def mesh_consensus_vote(glyph, threshold=0.95, min_drones=3):
    votes = [drone.validate_glyph(glyph) for drone in fleet]
    agreement = sum(votes) / len(votes)
    return agreement >= threshold and len(votes) >= min_drones