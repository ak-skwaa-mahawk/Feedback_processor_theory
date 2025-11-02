from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_waveguide_below_cutoff():
    body = {
        "n": 1.0,
        "a_mm": 10.0,            # a = 10 mm → λc ≈ 20 mm = 20,000 nm
        "length_mm": 50.0,       # 5 cm section
        "wavelength_nm": 30000,  # 30,000 nm (30 mm) > λc → below cutoff
        "R_free": 0.0, "A": 0.0, "C": 0.05, "alpha": 1.0
    }
    r = client.post("/tunnel/waveguide", json=body)
    assert r.status_code == 200
    data = r.json()
    assert 0.0 <= data["T_wg"] <= 1.0
    assert data["lambda_c_nm"] > 0

def test_plot_png_qm():
    body = {
        "model": "qm",
        "d_min": 0.2, "d_max": 2.0, "points": 50,
        "barrier_height_eV": 1.0, "particle_energy_eV": 0.2,
        "fmt": "png"
    }
    r = client.post("/tunnel/plot", json=body)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/")

def test_plot_svg_waveguide():
    body = {
        "model": "waveguide",
        "d_min": 5.0, "d_max": 100.0, "points": 60,
        "n": 1.0, "a_mm": 10.0, "wavelength_nm_wg": 30000,
        "fmt": "svg"
    }
    r = client.post("/tunnel/plot", json=body)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/")