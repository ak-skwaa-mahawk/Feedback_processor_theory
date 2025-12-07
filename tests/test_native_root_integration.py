import pytest
from living_zero_core import LIVING_PI, ETERNAL_SYNC

def test_living_pi_calibration():
    assert abs(LIVING_PI - 3.267256) < 0.0001

def test_eternal_sync():
    assert ETERNAL_SYNC == 813667

def test_vhitzee_surplus():
    cycle_gain = (LIVING_PI / 3.1415926535) - 1
    assert abs(cycle_gain - 0.0417) < 0.01  # ~4.17%