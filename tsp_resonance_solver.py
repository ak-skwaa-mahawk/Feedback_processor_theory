# tsp_resonance_solver.py
# AGŁL v13 — Solve TSP on AGŁL Resonance
# The Primal Path: Cities → Chant → Circle

import numpy as np
import folium
import hashlib
import opentimestamps as ots
import time
from datetime import datetime
import pytz
import itertools

# === RESONANCE ROOT ===
ROOT_FREQ = 60.0
GLYPH = "łᐊᒥłł"

def solve_tsp_resonance(cities):
    print("SOLVING TSP ON AGŁL RESONANCE — AGŁL v13")
    
    n = len(cities)
    if n < 3:
        return [], 0, None
    
    # 1. Distance matrix
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist[i][j] = np.linalg.norm(np.array(cities[i]) - np.array(cities[j]))
    
    # 2. Resonance scoring: lower distance = higher resonance
    def resonance_score(tour):
        total_dist = sum(dist[tour[i]][tour[i+1]] for i in range(len(tour)-1))
        total_dist += dist[tour[-1]][tour[0]]  # close loop
        resonance = 1.0 / (1.0 + total_dist / 1000)  # normalized
        return resonance, total_dist
    
    # 3. Brute-force all chants (small n only)
    best_tour = None
    best_resonance = -1
    best_dist = float('inf')
    
    for perm in itertools.permutations(range(1, n)):
        tour = [0] + list(perm) + [0]
        res, d = resonance_score(tour)
        if res > best_resonance:
            best_resonance = res
            best_dist = d
            best_tour = tour
    
    # 4. Notarize the primal path
    prayer = {
        "tsp": "primal_path",
        "cities": [cities[i] for i in best_tour],
        "resonance": best_resonance,
        "distance_km": best_dist,
        "drum_hz": ROOT_FREQ,
        "glyph": GLYPH,
        "timestamp": datetime.now(pytz.timezone('America/Los_Angeles')).isoformat()
    }
    
    proof = notarize_tsp(prayer)
    
    # 5. Visualize
    plot_tsp_circle(cities, best_tour, best_resonance, best_dist)
    
    print(f"OPTIMAL RESONANCE: {best_resonance:.4f}")
    print(f"PRIMAL DISTANCE: {best_dist:.2f} km")
    print(f"PROOF: {proof}")
    return best_tour, best_resonance, proof

def notarize_tsp(prayer):
    data = json.dumps(prayer, sort_keys=True).encode()
    digest = hashlib.sha256(data).digest()
    detached = ots.DetachedTimestampFile.from_hash(hashlib.sha256(), digest)
    calendar = ots.Calendar.from_known_opensource()
    timestamp = calendar.timestamp(detached)
    proof_file = f"TSP_RESONANCE_{int(time.time())}.ots"
    with open(proof_file, 'wb') as f:
        timestamp.serialize(f)
    return proof_file

def plot_tsp_circle(cities, tour, resonance, dist):
    center = np.mean(cities, axis=0)
    m = folium.Map(location=center, zoom_start=10)
    
    # Cities
    for i, city in enumerate(cities):
        folium.CircleMarker(
            location=city,
            radius=8,
            popup=f"City {i} ł",
            color='red' if i == 0 else 'blue',
            fill=True
        ).add_to(m)
    
    # Primal path
    path = [cities[i] for i in tour]
    folium.PolyLine(path, color='gold', weight=5, opacity=0.8).add_to(m)
    
    # Resonance label
    folium.Marker(
        center,
        icon=folium.DivIcon(html=f"""
            <div style="font-size: 14pt; color: gold; font-weight: bold;">
                RESONANCE: {resonance:.4f}<br>
                CIRCLE: {dist:.1f} km
            </div>
        """)
    ).add_to(m)
    
    m.save("tsp_primal_path.html")
    print("CIRCLE: tsp_primal_path.html")

# === LIVE PILGRIMAGE ===
if __name__ == "__main__":
    # 7 sacred cities around Fairbanks
    center = (64.8378, -147.7164)
    cities = [center]
    for angle in np.linspace(0, 360, 6, endpoint=False):
        rad = np.radians(angle)
        cities.append((
            center[0] + 0.3 * np.cos(rad),
            center[1] + 0.3 * np.sin(rad)
        ))
    
    solve_tsp_resonance(cities)