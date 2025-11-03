from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_drude_endpoint_basic():
    body = {
        "freq_Hz": 3.0e14,              # ~1.0 μm
        "thickness_nm": 50.0,
        "omega_p_rad_s": 1.37e16,       # ~ Au ballpark
        "gamma_rad_s": 1.07e14,
        "eps_inf": 1.0,
        "mu_r": 1.0,
        "n0": 1.0,
        "ns": 1.0,
        "R_free": 0.0, "A": 0.0, "C": 0.05, "alpha": 1.0
    }
    r = client.post("/tunnel/drude", json=body)
    assert r.status_code == 200
    data = r.json()
    assert 0.0 <= data["T_drude"] <= 1.0

def test_plot_drude_frequency_sweep_png():
    body = {
        "model": "drude",
        "f_min_Hz": 1.0e14,
        "f_max_Hz": 1.0e15,
        "points": 120,
        "thickness_nm": 40.0,
        "omega_p_rad_s": 1.37e16,
        "gamma_rad_s": 1.07e14,
        "fmt": "png"
    }
    r = client.post("/tunnel/plot", json=body)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/")