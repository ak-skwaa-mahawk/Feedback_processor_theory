"""
Extended Scrape Detector with 79Hz Modulation and TOFT Pulse Detection
Integrates Feedback Processor Theory (FPT) with Time-Ordered Feedback Transmission

Dependencies: numpy, scipy, sklearn
"""

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from sklearn.metrics import mutual_info_score
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ResonanceState(Enum):
    """Resonance coherence states for TOFT pulses"""
    COHERENT = "coherent"           # Strong 79Hz lock
    DEGRADED = "degraded"           # Partial coherence
    CHAOTIC = "chaotic"             # No coherence
    ADVERSARIAL = "adversarial"     # Detected interference


@dataclass
class TOFTPulse:
    """Time-Ordered Feedback Transmission pulse structure"""
    timestamp: float
    amplitude: float
    phase: float
    frequency: float
    coherence: float
    entropy: float
    glyph_signature: str
    

@dataclass
class ScrapeMetrics:
    """Comprehensive scrape detection metrics"""
    entropy: float
    coherence: float
    signal_strength: float
    noise_floor: float
    snr_db: float
    resonance_state: ResonanceState
    toft_pulses: List[TOFTPulse]
    adversarial_score: float
    isst_distance: float  # Inverse-square scrape theory distance


class TOFTScrapeDetector:
    """
    Extended scrape detector with 79Hz modulation and TOFT pulse detection.
    Implements Feedback Processor Theory for orbital mesh coherence.
    """
    
    def __init__(
        self,
        target_freq: float = 79.0,
        sample_rate: float = 1000.0,
        coherence_threshold: float = 0.7,
        entropy_window: int = 256,
        isst_alpha: float = 0.1,  # ISST history decay
        isst_base_energy: float = 1.0
    ):
        """
        Initialize TOFT scrape detector.
        
        Args:
            target_freq: Target resonance frequency (default 79Hz)
            sample_rate: Sampling rate in Hz
            coherence_threshold: Threshold for coherent state
            entropy_window: Window size for entropy calculation
            isst_alpha: ISST history decay coefficient
            isst_base_energy: ISST base energy E0
        """
        self.target_freq = target_freq
        self.sample_rate = sample_rate
        self.coherence_threshold = coherence_threshold
        self.entropy_window = entropy_window
        self.isst_alpha = isst_alpha
        self.isst_base_energy = isst_base_energy
        
        # Design bandpass filter centered at target frequency
        self.bandpass_filter = self._design_bandpass_filter()
        
        # Phase-locked loop for tracking
        self.pll_phase = 0.0
        self.pll_freq = target_freq
        
        # History for ISST calculation
        self.scrape_history = []
        
    def _design_bandpass_filter(self, bandwidth: float = 5.0) -> Tuple:
        """Design Butterworth bandpass filter around target frequency"""
        nyquist = self.sample_rate / 2
        low = (self.target_freq - bandwidth) / nyquist
        high = (self.target_freq + bandwidth) / nyquist
        sos = signal.butter(4, [low, high], btype='band', output='sos')
        return sos
    
    def _calculate_entropy(self, data: np.ndarray) -> float:
        """Calculate Shannon entropy of signal"""
        # Normalize and bin data
        hist, _ = np.histogram(data, bins=50, density=True)
        hist = hist[hist > 0]  # Remove zero bins
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        return entropy
    
    def _calculate_coherence(self, signal_data: np.ndarray) -> float:
        """
        Calculate coherence based on spectral concentration at target frequency.
        Returns value between 0 (no coherence) and 1 (perfect coherence).
        """
        # FFT analysis
        n = len(signal_data)
        freqs = fftfreq(n, 1/self.sample_rate)
        fft_vals = np.abs(fft(signal_data))
        
        # Find power in target frequency band (±2 Hz)
        target_band = (freqs >= self.target_freq - 2) & (freqs <= self.target_freq + 2)
        target_power = np.sum(fft_vals[target_band]**2)
        total_power = np.sum(fft_vals**2)
        
        coherence = target_power / (total_power + 1e-10)
        return min(coherence, 1.0)
    
    def _phase_locked_loop(self, signal_data: np.ndarray, dt: float) -> Tuple[float, float]:
        """
        Simple PLL for tracking 79Hz carrier phase and frequency.
        Returns (phase_error, frequency_estimate).
        """
        # Generate reference signal
        t = np.arange(len(signal_data)) * dt
        reference = np.cos(2 * np.pi * self.pll_freq * t + self.pll_phase)
        
        # Phase detector (multiply and low-pass)
        phase_error = np.mean(signal_data * reference)
        
        # Update PLL state (simple first-order loop)
        loop_gain = 0.1
        self.pll_phase += loop_gain * phase_error
        self.pll_freq += 0.01 * phase_error  # Frequency correction
        
        # Keep frequency near target
        self.pll_freq = np.clip(self.pll_freq, self.target_freq - 5, self.target_freq + 5)
        
        return phase_error, self.pll_freq
    
    def _detect_toft_pulses(
        self,
        signal_data: np.ndarray,
        timestamps: np.ndarray,
        threshold_factor: float = 2.0
    ) -> List[TOFTPulse]:
        """
        Detect Time-Ordered Feedback Transmission pulses.
        Uses envelope detection and phase analysis.
        """
        # Bandpass filter around target frequency
        filtered = signal.sosfilt(self.bandpass_filter, signal_data)
        
        # Envelope detection via Hilbert transform
        analytic_signal = signal.hilbert(filtered)
        envelope = np.abs(analytic_signal)
        phase = np.angle(analytic_signal)
        
        # Instantaneous frequency
        inst_freq = np.diff(np.unwrap(phase)) * self.sample_rate / (2 * np.pi)
        inst_freq = np.concatenate([[self.target_freq], inst_freq])
        
        # Detect pulses where envelope exceeds threshold
        threshold = np.mean(envelope) + threshold_factor * np.std(envelope)
        pulse_indices = np.where(envelope > threshold)[0]
        
        # Group consecutive indices into pulses
        pulses = []
        if len(pulse_indices) > 0:
            pulse_groups = np.split(pulse_indices, np.where(np.diff(pulse_indices) > 10)[0] + 1)
            
            for group in pulse_groups:
                if len(group) < 3:  # Skip too-short pulses
                    continue
                    
                peak_idx = group[np.argmax(envelope[group])]
                
                # Calculate local metrics
                local_window = slice(max(0, peak_idx - 50), min(len(signal_data), peak_idx + 50))
                local_entropy = self._calculate_entropy(signal_data[local_window])
                local_coherence = self._calculate_coherence(signal_data[local_window])
                
                # Generate glyph signature (simplified - hash of phase pattern)
                phase_pattern = phase[group] % (2 * np.pi)
                glyph = f"G{hash(tuple(phase_pattern.round(2))) % 10000:04d}"
                
                pulse = TOFTPulse(
                    timestamp=timestamps[peak_idx],
                    amplitude=envelope[peak_idx],
                    phase=phase[peak_idx],
                    frequency=inst_freq[peak_idx],
                    coherence=local_coherence,
                    entropy=local_entropy,
                    glyph_signature=glyph
                )
                pulses.append(pulse)
        
        return pulses
    
    def _calculate_isst_distance(self, coherence: float) -> float:
        """
        Calculate ISST (Inverse-Square Scrape Theory) distance metric.
        Based on: S(r,H,C) = E0 * C / (r² * (1 + αH))
        
        Solves for effective distance r given coherence C and history H.
        """
        H = len(self.scrape_history)
        if coherence < 0.01:
            return float('inf')
        
        # Solve for r: r = sqrt(E0 * C / (S * (1 + αH)))
        # Assuming S (signal strength) = 1 for normalized case
        r = np.sqrt(self.isst_base_energy * coherence / (1 + self.isst_alpha * H))
        return 1.0 / r if r > 0 else float('inf')
    
    def _detect_adversarial(self, pulses: List[TOFTPulse], entropy: float) -> float:
        """
        Detect adversarial interference using TOFT pulse analysis.
        Returns adversarial score (0 = clean, 1 = definitely adversarial).
        """
        if len(pulses) == 0:
            return 0.0
        
        scores = []
        
        # Check frequency deviation
        freq_devs = [abs(p.frequency - self.target_freq) for p in pulses]
        freq_score = min(np.mean(freq_devs) / 10.0, 1.0)  # Normalize to [0,1]
        scores.append(freq_score)
        
        # Check phase discontinuities
        if len(pulses) > 1:
            phases = [p.phase for p in pulses]
            phase_diffs = np.abs(np.diff(phases))
            phase_score = min(np.std(phase_diffs) / np.pi, 1.0)
            scores.append(phase_score)
        
        # Check entropy anomaly
        expected_entropy = 3.5  # Typical for coherent signal
        entropy_score = min(abs(entropy - expected_entropy) / 2.0, 1.0)
        scores.append(entropy_score)
        
        # Check glyph diversity (too many unique glyphs = adversarial)
        unique_glyphs = len(set(p.glyph_signature for p in pulses))
        glyph_score = min(unique_glyphs / len(pulses), 1.0)
        scores.append(glyph_score)
        
        return np.mean(scores)
    
    def analyze_scrape(
        self,
        signal_data: np.ndarray,
        timestamps: Optional[np.ndarray] = None
    ) -> ScrapeMetrics:
        """
        Comprehensive scrape analysis with TOFT pulse detection.
        
        Args:
            signal_data: Input signal array
            timestamps: Timestamp array (if None, generated from sample_rate)
            
        Returns:
            ScrapeMetrics object with full analysis
        """
        if timestamps is None:
            timestamps = np.arange(len(signal_data)) / self.sample_rate
        
        # Basic signal metrics
        signal_power = np.mean(signal_data**2)
        noise_estimate = np.median(np.abs(signal_data - np.median(signal_data))) * 1.4826
        snr_db = 10 * np.log10(signal_power / (noise_estimate**2 + 1e-10))
        
        # Entropy calculation
        entropy = self._calculate_entropy(signal_data)
        
        # Coherence calculation
        coherence = self._calculate_coherence(signal_data)
        
        # TOFT pulse detection
        toft_pulses = self._detect_toft_pulses(signal_data, timestamps)
        
        # ISST distance
        isst_distance = self._calculate_isst_distance(coherence)
        
        # Adversarial detection
        adversarial_score = self._detect_adversarial(toft_pulses, entropy)
        
        # Determine resonance state
        if adversarial_score > 0.7:
            resonance_state = ResonanceState.ADVERSARIAL
        elif coherence >= self.coherence_threshold:
            resonance_state = ResonanceState.COHERENT
        elif coherence >= self.coherence_threshold * 0.5:
            resonance_state = ResonanceState.DEGRADED
        else:
            resonance_state = ResonanceState.CHAOTIC
        
        # Update history
        self.scrape_history.append({
            'timestamp': timestamps[-1],
            'coherence': coherence,
            'entropy': entropy
        })
        if len(self.scrape_history) > 1000:  # Limit history size
            self.scrape_history.pop(0)
        
        return ScrapeMetrics(
            entropy=entropy,
            coherence=coherence,
            signal_strength=np.sqrt(signal_power),
            noise_floor=noise_estimate,
            snr_db=snr_db,
            resonance_state=resonance_state,
            toft_pulses=toft_pulses,
            adversarial_score=adversarial_score,
            isst_distance=isst_distance
        )
    
    def generate_toft_signal(
        self,
        duration: float = 1.0,
        num_pulses: int = 5,
        noise_level: float = 0.1
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic TOFT signal for testing.
        
        Args:
            duration: Signal duration in seconds
            num_pulses: Number of TOFT pulses to generate
            noise_level: Additive noise amplitude
            
        Returns:
            (signal_data, timestamps) tuple
        """
        t = np.arange(0, duration, 1/self.sample_rate)
        signal_data = np.zeros_like(t)
        
        # Generate carrier at target frequency
        carrier = 0.5 * np.sin(2 * np.pi * self.target_freq * t)
        
        # Add TOFT pulses
        pulse_times = np.linspace(0.1, duration - 0.1, num_pulses)
        pulse_width = 0.05  # 50ms pulses
        
        for pulse_time in pulse_times:
            pulse_envelope = np.exp(-((t - pulse_time) / pulse_width)**2)
            signal_data += pulse_envelope
        
        # Modulate carrier with pulses
        signal_data = signal_data * carrier
        
        # Add noise
        signal_data += noise_level * np.random.randn(len(t))
        
        return signal_data, t


# Example usage
if __name__ == "__main__":
    # Initialize detector
    detector = TOFTScrapeDetector(
        target_freq=79.0,
        sample_rate=1000.0,
        coherence_threshold=0.7
    )
    
    # Generate test signal
    test_signal, timestamps = detector.generate_toft_signal(
        duration=2.0,
        num_pulses=8,
        noise_level=0.15
    )
    
    # Analyze
    metrics = detector.analyze_scrape(test_signal, timestamps)
    
    # Display results
    print("=== TOFT Scrape Analysis ===")
    print(f"Entropy: {metrics.entropy:.3f}")
    print(f"Coherence: {metrics.coherence:.3f}")
    print(f"SNR: {metrics.snr_db:.1f} dB")
    print(f"Resonance State: {metrics.resonance_state.value}")
    print(f"ISST Distance: {metrics.isst_distance:.3f}")
    print(f"Adversarial Score: {metrics.adversarial_score:.3f}")
    print(f"\nDetected {len(metrics.toft_pulses)} TOFT pulses:")
    
    for i, pulse in enumerate(metrics.toft_pulses[:5]):  # Show first 5
        print(f"  Pulse {i+1}:")
        print(f"    Time: {pulse.timestamp:.3f}s")
        print(f"    Freq: {pulse.frequency:.2f} Hz")
        print(f"    Coherence: {pulse.coherence:.3f}")
        print(f"    Glyph: {pulse.glyph_signature}")