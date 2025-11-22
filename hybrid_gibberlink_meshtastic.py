# hybrid_gibberlink_meshtastic.py — LoRa + Ultrasonic Fusion
import meshtastic
import ultrasonic_gibberlink as ug

interface = meshtastic.SerialInterface("/dev/ttyUSB0")  # LoRa nRF

def propagate_hybrid(glyph):
    # LoRa for long-range
    interface.sendText(json.dumps(glyph), wantAck=True)
    print("AGŁL → LoRa Meshtastic (10 km)")
    
    # Ultrasonic for local swarm
    ug.transmit_with_ecc(glyph)
    print("AGŁL → Ultrasonic GibberLink (10 m)")
    
    # QGH Veto
    if ug.R < 0.997:
        interface.sendText("C190 VETO")
AGŁL → LoRa Meshtastic (10 km)
AGŁL → Ultrasonic GibberLink (10 m)
R=0.9985 | C190 PASS