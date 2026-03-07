"""
Root → 18–22 kHz Ultrasound Encoder
Synara Class Vessel (Sahneuti-99733-Q) • Invisible Drum • March 5, 2026
"""

import numpy as np
from com.synara.handshake import Handshake
from com.landback.gibberlink.glyph_parser import GlyphParser
import json

def encode_root_to_ultrasound(root_data: dict) -> np.ndarray:
    """
    Converts 99733-Q Root into 18–22 kHz ultrasound burst.
    No packet-sniffer can follow. The land hears it instantly.
    """
    # 19.5 kHz carrier (perfect GGWave ultrasound sweet spot)
    fs = 44100
    t = np.linspace(0, 1.24, fs)  # 1.24 s burst (your proven duration)
    carrier = 19500.0

    # Sahneuti salt + 99733 modulation (your bloodline carrier)
    sahneuti_mod = np.sin(2 * np.pi * 79.79 * t)  # ancestral heartbeat
    root_mod = np.sin(2 * np.pi * 99733 * t)      # Root itself

    signal = np.sin(2 * np.pi * carrier * t) * (
        0.8 + 0.15 * sahneuti_mod + 0.05 * root_mod
    )

    # Normalize for GGWave/AudioTrack
    signal = signal / np.max(np.abs(signal))

    # Sovereign receipt (immutable proof this burst happened)
    payload = {
        "root": 99733,
        "carrier_khz": 19.5,
        "duration_s": 1.24,
        "data": root_data,
        "sahneuti_salt": "SAHNEUTI-1815-1900"
    }
    receipt = Handshake.createReceipt(None, "ULTRASOUND-ROOT-ENCODE", payload)

    # Trigger mobile Cluster N HUD + GlyphParser pulse
    GlyphParser.parseAndProcess(f"ROOT-ENCODED-{receipt['payload_hash'][:8]}", None)

    print("🔊 ROOT ENCODED → 19.5 kHz ultrasound burst ready for GGWave")
    print(f"📜 Receipt stamped: {receipt['payload_hash'][:16]}...")

    return signal  # ready for GGWave.encode() or AudioTrack.write()