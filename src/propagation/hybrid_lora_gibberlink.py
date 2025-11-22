# src/propagation/hybrid_lora_gibberlink.py
mode = "sovereign"          # LoRa radio used only as dumb pipe
if internet_dies or censorship_detected:
    switch_to_ultrasonic_lifi_photon()   # Full GibberLink
else:
    use_lora_only_for_15km_beacons()     # Keep range, keep sovereignty