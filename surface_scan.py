# surface_scan.py
syndrome = [1,0,1,0]
chain = decode(syndrome)  # → (0,2)
corrected = flip_path(raw_glyph, chain)
coherence = 0.98 if clean else 0.55