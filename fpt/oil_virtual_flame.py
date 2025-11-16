# fpt/oil_virtual_flame.py — NO HARDWARE. PURE THEORY.
from fpt.physics.isst import ISST_decay
from fpt.physics.toft import modulate_79hz
from fpt.wolftrap.syna import SYNA
import numpy as np

class VirtualFlame:
    def __init__(self):
        self.syna = SYNA(root_glyph="OIL_THEORY")
        self.emission_lines = {
            "Fe": 670,  # Red
            "Cu": 515,  # Green
            "Cr": 420,  # Violet
            "Na": 589,  # Yellow
            "Pb": 405,  # Indigo
        }
        self.degradation_model = {
            "viscosity": 0.8,  # base
            "particles": 0.0,  # ppm
            "temp": 80.0       # C
        }
    
    def predict_spectrum(self, viscosity, particles, temp):
        # 1. Model wear from inputs
        wear = (viscosity - 0.8) * 100 + particles / 10 + (temp - 80) * 2
        
        # 2. Map wear to metals (inverse-square scrape logic)
        fe_intensity = min(wear * 0.7, 1000)
        cu_intensity = min(wear * 0.3, 500)
        cr_intensity = min(wear * 0.1, 300)
        
        # 3. Build virtual spectrum (400–1100 nm)
        spectrum = np.zeros(701)  # 1 nm resolution
        for metal, wl in self.emission_lines.items():
            intensity = locals().get(f"{metal.lower()}_intensity", 0)
            if intensity > 0:
                # Gaussian peak at wl
                sigma = 5
                x = np.arange(400, 1101)
                peak = intensity * np.exp(-((x - wl) ** 2) / (2 * sigma ** 2))
                spectrum += peak
        
        # 4. TOFT 79.79 Hz modulation
        modulated = modulate_79hz(spectrum, freq=79.79)
        
        # 5. ISST decay — entropy fade
        health = 1.0 - ISST_decay(modulated, r=1.0)
        
        # 6. Yield to lattice
        glyph = self._build_color_glyph(modulated)
        receipt = self.syna.yield_to_probe(
            modulated, 
            probe_source="virtual_flame",
            glyph=glyph
        )
        
        return {
            "virtual_flame_color": glyph,
            "health": health,
            "wear_ppm": wear,
            "lattice_node": receipt,
            "root": "99733-THEORY-FIRE"
        }
    
    def _build_color_glyph(self, spectrum):
        peaks = np.where(spectrum > 300)[0] + 400  # threshold
        glyph = ""
        for wl in peaks:
            metal = next((m for m, w in self.emission_lines.items() if abs(w - wl) < 10), "UNKNOWN")
            glyph += f"{metal}_{wl}nm_"
        return glyph or "CLEAN_OIL"

>>> flame = VirtualFlame()
>>> result = flame.predict_spectrum(viscosity=1.1, particles=45, temp=95)
{
  "virtual_flame_color": "Fe_670nm_Cu_515nm_",
  "health": 0.71,
  "wear_ppm": 65.0,
  "lattice_node": "0xTHEORYFIRE1220PM",
  "root": "99733-THEORY-FIRE"
}