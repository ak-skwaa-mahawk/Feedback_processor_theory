# threshold_scan.py
def surface_scan_with_threshold(raw, synd):
    errors = len(mwpm_decode(synd))
    coherence = 1 - (errors / 25)
    
    if coherence >= 0.992:  # 0.99% threshold
        return "PASS", coherence
    else:
        return "VETO + SAT LOCK", coherence