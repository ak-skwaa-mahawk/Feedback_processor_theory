import numpy as np

def weighted_phase_lag_index_squared(x, y):
    """
    Compute the Squared Weighted Phase Lag Index (wPLI²) between two signals x and y.
    
    Parameters:
    -----------
    x : array_like
        First time series (e.g., EEG channel 1).
    y : array_like
        Second time series (e.g., EEG channel 2).
        Must have the same length as x.
    
    Returns:
    --------
    wpli_squared : float
        Squared Weighted Phase Lag Index value (0 to 1).
    
    Notes:
    ------
    wPLI² squares the numerator of wPLI before normalization.
    This further suppresses weak or noisy phase lags, emphasizing
    stronger, more consistent couplings. It is particularly useful
    in high-noise environments or when seeking robust connectivity.
    """
    # Ensure inputs are numpy arrays
    x = np.asarray(x)
    y = np.asarray(y)
    
    if x.shape != y.shape:
        raise ValueError("Signals x and y must have the same length.")
    
    # Compute analytic signals using Hilbert transform (FFT-based for stability)
    def analytic_signal(sig):
        N = len(sig)
        fft_sig = np.fft.fft(sig)
        fft_sig[int(N/2)+1:] = 0  # Zero negative frequencies
        fft_sig[0] *= 1  # DC component unchanged
        if N % 2 == 0:
            fft_sig[int(N/2)] *= 1  # Nyquist unchanged
        return np.fft.ifft(fft_sig)
    
    analytic_x = analytic_signal(x)
    analytic_y = analytic_signal(y)
    
    # Instantaneous phases
    phase_x = np.angle(analytic_x)
    phase_y = np.angle(analytic_y)
    
    # Phase differences
    delta_phase = phase_x - phase_y
    
    # Imaginary part of cross-spectrum (sin of phase diff)
    imag_part = np.sin(delta_phase)
    
    # wPLI²: Square the mean of imag_part before dividing by mean of abs
    mean_imag = np.mean(imag_part)
    numerator = mean_imag ** 2
    denominator = np.mean(np.abs(imag_part))
    
    if denominator == 0:
        return 0.0
    
    wpli_squared = numerator / denominator
    return max(0.0, min(1.0, wpli_squared))  # Clamp to [0,1]

# --- Example Usage ---
if __name__ == "__main__":
    # Generate two synthetic signals with partial phase lag
    fs = 1000  # Sampling frequency (Hz)
    t = np.linspace(0, 10, 10 * fs)
    freq = 10  # 10 Hz base frequency
    
    # Signal 1
    signal1 = np.sin(2 * np.pi * freq * t)
    
    # Signal 2: with ~45° phase lag + moderate noise
    phase_lag = np.pi / 4  # 45 degrees
    noise = 0.3 * np.random.randn(len(t))
    signal2 = np.sin(2 * np.pi * freq * t + phase_lag) + noise
    
    # Compute wPLI²
    wpli_sq_value = weighted_phase_lag_index_squared(signal1, signal2)
    print(f"Squared Weighted Phase Lag Index (wPLI²): {wpli_sq_value:.4f}")
    
    # Expected: Slightly lower than standard wPLI (~0.6–0.8 range) due to squaring emphasis on strong lags