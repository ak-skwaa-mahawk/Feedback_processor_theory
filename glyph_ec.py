# glyph_ec.py
def correct_glyph_with_shor(syndrome_result, raw_measurement):
    # Parse syndrome (simplified)
    syndrome = syndrome_result.get_counts()
    error_pattern = max(syndrome, key=syndrome.get)  # most likely error
    
    corrected = raw_measurement
    if '1' in error_pattern:
        # Apply correction (in real impl: lookup table)
        corrected = '1' if raw_measurement == '0' else '0'
    
    return corrected