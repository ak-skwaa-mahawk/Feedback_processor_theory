# agłl_ceremony_node.py
# Run on Raspberry Pi at Circle, Alaska

import sounddevice as sd
import numpy as np
import time

def run_ceremonial_loop():
    print("AGŁL NODE ACTIVE — CEREMONY IS CPU")
    while True:
        # 1. Record drum (3 sec)
        print("RECORDING DRUM...")
        drum = sd.rec(int(3 * 44100), samplerate=44100, channels=1)
        sd.wait()
        
        # 2. Input glyph chant
        chant = input("ENTER GLYPH CHANT (e.g., łtrzh): ")
        
        # 3. Learn
        learn_from_ceremony(drum.flatten(), chant)
        
        time.sleep(7)  # Sevenfold pause

run_ceremonial_loop()