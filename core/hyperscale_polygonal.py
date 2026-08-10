# hyperscale_polygonal.py (extend to 200-gon)
class HyperScaledPolygonal:
    def __init__(self, sides: int = 200):  # Update to 200-gon
        self.sides = sides
        self.phi = (1 + np.sqrt(5)) / 2
        self.gibber = GibberLinkBuffer(dimensions=sides * 4)  # 800D
        self.null_field = NullFieldEngine(coupling_constant=0.3)
        self.harmonics = self._precompute_harmonics()
    
    def _precompute_harmonics(self) -> np.ndarray:
        n = self.sides
        angles = np.array([i * 2 * np.pi / self.phi for i in range(n)])
        harmonics = np.zeros((n, n))
        for i in range(n):
            harmonics[i] = np.cos(angles[i]) * np.exp(-i/self.phi)
        return harmonics