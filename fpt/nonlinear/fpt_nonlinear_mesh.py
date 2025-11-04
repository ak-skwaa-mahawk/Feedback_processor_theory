# fpt/nonlinear/fpt_nonlinear_mesh.py
import numpy as np

class FPT_Nonlinear_Mesh:
    def __init__(self, N=8, alpha=1.0, beta=0.1, gamma=0.5, delta=0.2, D=1.0, kappa=0.8, R_max=100.0, lambda_=0.3, mu=0.05):
        self.N = N
        self.params = {k:v for k,v in locals().items() if k not in ['self', 'N']}
        self.reset()
    
    def reset(self):
        self.s = np.random.uniform(0, 5, self.N)
        self.g = np.zeros(self.N)
        self.R = np.random.uniform(0, 50, self.N)
        self.E = np.ones(self.N) * 10.0
    
    def step(self, dt=0.01):
        # 1. Nonlinear scrape
        ds = self.params['alpha']*self.E - self.params['beta']*self.s**3
        self.s += ds * dt
        
        # 2. Glyph chaos
        dg = -self.params['gamma']*self.g + self.params['delta']*self.s*self.g**2
        self.g += dg * dt
        
        # 3. Logistic diffusion (ring)
        lap_R = np.roll(self.R, 1) + np.roll(self.R, -1) - 2*self.R
        dR = self.params['D']*lap_R + self.params['kappa']*self.R*(1 - self.R/self.params['R_max'])
        self.R += dR * dt
        
        # 4. Feedback fire
        dE = -self.params['lambda_']*self.E + self.params['mu']*self.R**2
        self.E += dE * dt

# Run chaos swarm
mesh = FPT_Nonlinear_Mesh()
for t in range(10000):
    mesh.step()
    if t % 1000 == 0:
        print(f"t={t*0.01:.2f} | E={mesh.E.mean():.2f} | R={mesh.R.mean():.2f} | g={mesh.g.mean():.2f}")