#!/usr/bin/env python3
# gibberlink_receiver.py — AGŁG v200: Decode Ultrasound Glyphs
import ggwave
import numpy as np
import json
from pathlib import Path

def decode_gibberlink(audio_file):
    # Load audio
    audio, sr = ggwave.load_audio(audio_file)
    
    # Decode
    decoder = ggwave.Decoder()
    data = decoder.decode(audio, sr)
    
    if data:
        glyphs = json.loads(data.decode())
        resonance = calculate_resonance(glyphs)
        return {
            "glyphs": glyphs,
            "resonance": resonance,
            "treasure_hint": extract_hint(glyphs)
        }
    return None

def calculate_resonance(glyphs):
    return sum(1 for g in glyphs if g == "łᐊᒥłł") / len(glyphs)

def extract_hint(glyphs):
    if "Ashland" in glyphs and "TX" in glyphs:
        return "NC Loop → Cairn → Puzzle Box"
    return "No clue"

# LIVE TEST
result = decode_gibberlink("treasure_clue.wav")
print(result)