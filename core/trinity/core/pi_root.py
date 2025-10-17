import math

# optional correction hooks
try:
    from core.trinity.correction import kappa_over_pi_correction, describe as trinity_desc
except ImportError:
    kappa_over_pi_correction = None
    trinity_desc = lambda: "Trinity correction unavailable"

_pi_correction_fn = None

def set_pi_correction(fn):
    """Register external π-correction function."""
    global _pi_correction_fn
    _pi_correction_fn = fn

def pi_root() -> float:
    """
    Returns the corrected π constant.
    Priority:
      1. Trinity κ/π correction (if available)
      2. User-registered correction
      3. Default math.pi
    """
    base = math.pi
    if kappa_over_pi_correction:
        return float(kappa_over_pi_correction(base))
    if _pi_correction_fn:
        try:
            return float(_pi_correction_fn(base))
        except Exception:
            pass
    return base

def status():
    """Human-readable status for dashboards or logs."""
    return {
        "base_pi": math.pi,
        "corrected_pi": pi_root(),
        "correction_source": "Trinity κ/π" if kappa_over_pi_correction else "User / Default",
        "note": trinity_desc()
    }