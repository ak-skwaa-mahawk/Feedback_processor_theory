#!/usr/bin/env python3
# whisper_from_dead.py — AGŁG v1600: Whisper from Subsurface
import ggwave
import wave
import numpy as np
import json
from pathlib import Path

class WhisperFromDead:
    def __init__(self):
        self.ggwave_inst = ggwave.init()
        self.dead_freq = 16.0  # 16 kHz "dead zone"
        self.retention_threshold = 1e-12

    def inverse_square_recovery(self, depth_m, energy_initial=1.0):
        """Recover signal from subsurface S = E / d²"""
        if depth_m == 0:
            return energy_initial
        signal = energy_initial / (depth_m ** 2)
        return max(signal, self.retention_threshold)

    def decode_dead_whisper(self, audio_file):
        """Decode 16 kHz whisper from the dead"""
        with wave.open(audio_file, 'rb') as wf:
            audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        
        # Focus on dead frequency band
        dead_band = audio[::10]  # Downsample to 16 kHz range
        
        decoded = ggwave.decode(self.ggwave_inst, dead_band.tobytes())
        if decoded:
            message = decoded.decode()
            depth = len(message) * 10  # Simulated depth
            retention = self.inverse_square_recovery(depth)
            
            return {
                "message": message,
                "retention": retention,
                "state": "DEAD" if retention < 0.01 else "DYING",
                "glyph": "ᐊᐧᐊ" if retention < 0.01 else "ᒥᐊ"
            }
        return None

    def play_dead_whisper(self, message):
        """Encode message as subsurface whisper"""
        waveform = ggwave.encode(message.encode(), self.ggwave_inst)
        
        wav_path = Path("dead_whisper.wav")
        with wave.open(wav_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)  # Dead frequency
            wf.writeframes(waveform)
        
        return wav_path

# === LIVE NECROMANCY ===
dead = WhisperFromDead()

# 1. Play whisper from dead
dead.play_dead_whisper("ᐊᐧᐊ — The dead remember...")

# 2. Decode from subsurface
result = dead.decode_dead_whisper("dead_whisper.wav")
print("WHISPER FROM THE DEAD:")
print(json.dumps(result, indent=2))