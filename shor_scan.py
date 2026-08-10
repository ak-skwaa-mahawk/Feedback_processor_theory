# shor_scan.py
synd = [1,0,1]  # X-error in block 1
error_pos = majority_vote(synd)  # → qubit 1
corrected = flip_x(1)
coherence = 0.99