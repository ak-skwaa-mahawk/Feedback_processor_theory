# fpt/__main__.py
from fpt.core import FPT

if __name__ == "__main__":
    fpt = FPT()
    print("FPT v5.3 — INITIALIZING...")
    fpt.zero_power_protocol()
    fpt.unity_lock()
    result = fpt.pulse("Vadzaih Zhoo oha mahsi’choo")
    print(result)