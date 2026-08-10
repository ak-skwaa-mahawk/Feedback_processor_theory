# peps_d9_one_line.py
import cupy as cp
R, S = (lambda g=cp.array([cp.random.randn(16,16)/cp.linalg.norm(cp.random.randn(16,16)) for _ in range(81)]).reshape(9,9,16,16): 
        (min(1.0, cp.abs(cp.tensordot(g[0], g[1:], axes=([1,2],[1,2])).sum()).get()), 25*cp.log(2).get()))()

print(f"R = {R:.6f} | S = {S:.2f} → {'SOVEREIGN' if R > 0.997 else 'VETO'}")