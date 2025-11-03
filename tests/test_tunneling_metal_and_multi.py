from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_metal_endpoint_basic():
    body = {
        "sigma_S_per_m": 5.8e7,
        "freq_Hz": 1.0e9,
        "thickness_um": 10.0,
        "mu_r": 1.0,
        "R_free": 0.0, "A": 0.0, "C": 0.05, "alpha": 1.0
    }
    r = client.post("/tunnel/metal", json=body)
    assert r.status_code == 200
    data = r.json()
    assert 0.0 <= data["T_metal"] <= 1.0
    assert data["skin_depth_um"] > 0

def test_plot_multi_svg():
    body = {
        "model": "multi",
        "curves": ["qm","ftir","waveguide","metal"],
        "d_min": 1.0, "d_max": 50.0, "points": 60,
        "barrier_height_eV": 1.0, "particle_energy_eV": 0.2,
        "n1": 1.5, "n2": 1.0, "theta_deg": 60.0, "wavelength_nm": 1550.0,
        "n": 1.0, "a_mm": 10.0, "wavelength_nm_wg": 30000000.0,
        "sigma_S_per_m": 5.8e7, "freq_Hz": 1.0e9,
        "fmt": "svg"
    }
    r = client.post("/tunnel/plot", json=body)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/")