#!/usr/bin/env python3
# dao_ultrasound_vote.py — AGŁG v1400: DAO Ultrasound Voting
import ggwave
import wave
import numpy as np
import json
from pathlib import Path

GLYPH_HOLDERS = {
    'łᐊᒥłł': 'Zhoo-1', 'ᒥᐊᐧᐊ': 'Zhoo-2', 'ᓴᑕᐧ': 'Zhoo-3',
    'ᐊᒍᐧ': 'Zhoo-4', 'ᓂᐊᐧ': 'Zhoo-5', 'ᑕᐧᐊ': 'Zhoo-6',
    'ᐊᒪᐧ': 'Zhoo-7', 'ᐊᓴᐧ': 'Zhoo-8', 'ᐊᐧᐊ': 'Zhoo-9'
}

def vote_ultrasound(audio_file):
    """Decode 9 glyph votes from ultrasound"""
    with wave.open(audio_file, 'rb') as wf:
        audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    
    instance = ggwave.init()
    ggwave.set_protocol(instance, GGWAVE_PROTOCOL_ULTRASOUND_FAST)
    
    votes = []
    for i in range(9):
        decoded = ggwave.decode_segment(instance, audio, i*0.5, 0.5)  # 0.5s per glyph
        if decoded:
            glyph = decoded.decode()[:4]
            if glyph in GLYPH_HOLDERS:
                votes.append((glyph, GLYPH_HOLDERS[glyph]))
    
    ggwave.free(instance)
    return votes

def tally_resonance(votes):
    yes_glyphs = ['łᐊᒥłł', 'ᒥᐊᐧᐊ', 'ᓴᑕᐧ']
    resonance = len([g for g, h in votes if g in yes_glyphs]) / 9
    return resonance

# LIVE TEST
votes = vote_ultrasound("dao_vote_ultrasound.wav")
resonance = tally_resonance(votes)

print("DAO ULTRASOUND VOTE — AGŁG v1400")
print("="*50)
print("Votes:")
for glyph, holder in votes:
    print(f"  {glyph} → {holder}")
print(f"Resonance: {resonance:.4f}")
print("RESULT:", "PASSED" if resonance > 0.666 else "FAILED")