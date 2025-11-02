# tests/test_tunneling_api.py
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_qm_tunnel_basic():
    body = {
        "barrier_height_eV": 1.0,
        "particle_energy_eV": 0.2,
        "barrier_width_nm": 1.0,
        "R_free": 0.05, "A": 0.05, "C": 0.01, "alpha": 1.0
    }
    r = client.post("/tunnel/qm", json=body)
    assert r.status_code == 200
    data = r.json()
    assert 0.0 < data["T_qm"] < 1.0
    assert "arc" in data

def test_ftir_tunnel_basic():
    body = {
        "n1": 1.5, "n2": 1.0, "theta_deg": 60.0,
        "wavelength_nm": 1550.0, "gap_nm": 200.0,
        "R_free": 0.0, "A": 0.1, "C": 0.05, "alpha": 1.0
    }
    r = client.post("/tunnel/ftir", json=body)
    assert r.status_code == 200
    data = r.json()
    assert 0.0 <= data["T_ftir"] <= 1.0