def residual_reconstruct(chunks, H, bp_decoder, iterations=20):
    """Residual-only BP reconstruction with sparse factor graph."""
    for _ in range(iterations):
        for i, chunk in enumerate(chunks):
            if chunk.confidence > 0.8:
                continue
            # BP on corrupted positions only
            llr = np.zeros(len(chunk.data))
            llr[chunk.mask] = chunk.reconstructed[chunk.mask] - chunk.data[chunk.mask]
            updated = bp_decoder.decode(llr)
            chunk.reconstructed[chunk.mask] = chunk.data[chunk.mask] + updated[chunk.mask]
            chunk.confidence = min(1.0, chunk.confidence + 0.1)
    return chunks