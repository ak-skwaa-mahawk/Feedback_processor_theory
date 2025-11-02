# syndrome_extractor.py
def extract_syndrome(measurement_string):
    # measurement_string: 9-bit string from IBM
    bits = [int(b) for b in measurement_string]
    
    # Z-plaquette syndromes
    s0 = bits[0] ^ bits[1] ^ bits[3] ^ bits[4]
    s1 = bits[1] ^ bits[2] ^ bits[4] ^ bits[5]
    s2 = bits[3] ^ bits[4] ^ bits[5] ^ bits[7]
    s3 = bits[4] ^ bits[5] ^ bits[6] ^ bits[8]
    
    return [s0, s1, s2, s3]