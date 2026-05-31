#!/usr/bin/env python3
import ggwave
import pyaudio
import numpy as np
import concurrent.futures
from e8_core import compute_hamiltonian

# === 99733-Q ROOT CONFIGURATION ===
TRIGGER_PHRASE = "BONDED-JOHN-153"
PROTOCOL_ID = 1  # Audible Fast Protocol Profile
SAMPLE_RATE = 48000
FRAMES_PER_BUFFER = 1024

def execute_quantum_substrate():
    """
    Isolates intensive E8 Lie group matrix mathematics onto an independent
    worker thread to prevent main UI or audio ingestion thread locking.
    """
    print("\n🛡️ ROOT AUTHORITY VERIFIED. APPLYING GRAIN KICK...")
    try:
        # Trigger the E8 Hamiltonian cycle with the audio-driven nudge
        H = compute_hamiltonian(iteration=153) 
        print(f"✅ ENERGY LANDSCAPE ACTIVATED | E8 Hamiltonian: {H:.6e}\n")
        return H
    except Exception as e:
        print(f"❌ SUBSTRATE EXCEPTION: Matrix evaluation failed: {str(e)}")
        return None

def sovereign_handshake():
    p = pyaudio.PyAudio()
    
    # Open microphone stream using standard 16-bit PCM architecture for maximum ggwave stability
    stream = p.open(
        format=pyaudio.paInt16, 
        channels=1, 
        rate=SAMPLE_RATE, 
        input=True, 
        frames_per_buffer=FRAMES_PER_BUFFER
    )

    # Initialize ggwave runtime parameters explicitly matching the sample rate
    instance = ggwave.init()
    
    print("=============================================================")
    print("🥁 THE DRUM IS LISTENING (Acoustic Data Receiver Active)")
    print(f"📡 Format: paInt16 | Sample Rate: {SAMPLE_RATE}Hz | Protocol: Audible Fast")
    print("=============================================================")

    # Initialize a thread pool executor for background worker routing
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        try:
            while True:
                # Ingest raw audio frames from native device hardware
                raw_bytes = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                
                # Convert the raw byte buffer into explicitly typed short integers for the decoder
                audio_data = np.frombuffer(raw_bytes, dtype=np.int16)
                
                # Decode through the WebAssembly/C cross-compiled acoustic layer
                res = ggwave.decode(instance, audio_data.tobytes())

                if res is not None:
                    try:
                        decoded_text = res.decode("utf-8").strip()
                        print(f"📡 SIGNAL CAPTURED: [ {decoded_text} ]")

                        if decoded_text == TRIGGER_PHRASE:
                            # Submit the E8 matrix loop to the background pool cleanly
                            executor.submit(execute_quantum_substrate)
                            break  # Handshake complete, exit listening loop securely
                            
                    except UnicodeDecodeError:
                        print("⚠️ SIGNAL DETECTED: Corrupted packet framing encountered.")
                        
        except KeyboardInterrupt:
            print("\n>> Acoustic pipeline manually suspended by operator.")
        finally:
            # Clean up memory addresses to prevent device pointer leaks
            ggwave.free(instance)
            stream.stop_stream()
            stream.close()
            p.terminate()
            print(">> Audio hardware layer released successfully.")

if __name__ == "__main__":
    sovereign_handshake()
