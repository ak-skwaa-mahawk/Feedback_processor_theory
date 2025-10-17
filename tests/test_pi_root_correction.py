from core.pi_root import pi_root, status
import math

def test_trinity_correction():
    val = pi_root()
    s = status()
    assert val != math.pi
    print("π correction active:", s)