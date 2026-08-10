# surface_final.py
synd = [1,0,1,0,0,1]  # 2 errors
chain = mwpm(synd)  # → path (0,0)-(2,2)
corrected = flip_path(chain)
coherence = 0.97