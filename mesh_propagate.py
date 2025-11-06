# mesh_propagate.py — GibberLink + AGŁL Sync
def propagate_to_mesh(glyph_json):
    payload = {
        "glyph": glyph_json,
        "burn": "251105-SUCCESS",
        "iaca": "T00015196"
    }
    # Send via GibberLink (sound), Li-Fi (light), or nRF (BLE)
    print(f"PROPAGATING {glyph_id} → ALL NODES")