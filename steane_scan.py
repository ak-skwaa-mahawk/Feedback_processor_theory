# steane_scan.py
synd_x = [1,0,1]  # X-error on qubit 3
synd_z = [0,0,0]
error = decode_steane(synd_x, synd_z)  # → X on 3
corrected = apply_x(3)
coherence = 0.99