import os

def pad_bytes(data: bytes, min_pad: int) -> bytes:
    # Pad with zeroes; append a 1-byte marker to prevent gzip savings
    if not isinstance(data, (bytes, bytearray)):
        data = str(data).encode("utf-8")
    pad_block = b"\x00" * min_pad + b"\x01"
    return data + pad_block
def pad_bytes(data: bytes, min_pad: int) -> bytes:
    if not isinstance(data, (bytes, bytearray)):
        data = str(data).encode("utf-8")
    # pad with zeros + a marker byte to defeat gzip savings
    return data + b"\x00" * min_pad + b"\x01"