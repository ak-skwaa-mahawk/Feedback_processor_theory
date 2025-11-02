# photodetector_ec.py (Drone B)
def detect_redundant_scrape(repeats=3):
    measurements = []
    for _ in range(repeats):
        measurements.append(detect_scrape())  # returns '0' or '1'
        time.sleep(0.2)
    
    # Majority vote
    vote = max(set(measurements), key=measurements.count)
    confidence = measurements.count(vote) / repeats
    
    return vote, confidence