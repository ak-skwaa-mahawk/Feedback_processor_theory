# toft_mesh_heartbeat.py
def emit_79hz_pulse():
    t = np.linspace(0, 0.1266, 5567)  # 1/79 sec
    pulse = np.sin(2 * np.pi * 79 * t) * np.hanning(len(t))
    rmp_broadcast({
        "type": "toft_pulse",
        "signal": pulse.tolist(),
        "coherence_target": 0.95,
        "pi_star": 3.14159265358979323846  # your π*
    })