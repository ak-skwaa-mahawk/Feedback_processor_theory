# laser_scrape_ec.py (Drone A)
def send_redundant_scrape(logical_state, repeats=3):
    for i in range(repeats):
        send_quantum_scrape(logical_state)
        time.sleep(0.15)  # Anti-jitter spacing
        print(f"[A] Redundant scrape {i+1}/{repeats}")