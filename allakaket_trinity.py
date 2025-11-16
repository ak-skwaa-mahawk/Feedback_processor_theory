# === BLOODLINE UPGRADE: ALLAKAKET TRINITY ===
def allakaket_trinity_mod(signal, fs):
    # Encode photo metadata + names as sub-audible pulse
    trinity = "CHIEF_MOSES_ELLEN_CLARA_ALLAKAKET_GWICHIN_1930S"
    trinity_bytes = trinity.encode()
    
    # Embed as 0.1 Hz pulse train (below human hearing)
    t = np.arange(len(signal)) / fs
    mod = np.sum([np.sin(2 * np.pi * 0.1 * i * t) for i in range(1, 4)], axis=0) / 3
    
    # Mix at -40 dB
    signal = signal + 0.01 * mod * np.max(np.abs(signal))
    return signal

# === FINAL VESTING COMMAND (WITH ALLAKAKET) ===
signal, t = generate_control_wave()
signal = allakaket_trinity_mod(signal, 44100)
signal_cmd = embed_vesting_command(signal, 44100)

wavfile.write('FPT_VESTING_COMMAND_ALLAKAKET.wav', 44100, signal_cmd)
print("ALLAKAKET BLOODLINE EMBEDDED: FPT_VESTING_COMMAND_ALLAKAKET.wav")