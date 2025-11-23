# src/propagation/gwichin_arctic.py
def gwichin_drum_carrier(freq=60.0, temperature=-50):
    # Frozen air has ~400 m/s sound speed → perfect ultrasonic reflector
    wavelength = 400 / freq
    reflection_gain = 10 ** (temperature / -10)  # empirical elder data
    return wavelength, reflection_gain

def grandmother_silence_veto(network_coherence):
    if elder_node.resonance < 0.997:
        trigger_global_silence()  # entire mesh drops to 0 dB instantly
        log("Grandmother veto engaged — bad story killed")
