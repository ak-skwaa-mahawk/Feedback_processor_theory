"""
Flame Adapter - Bridges Synara-core flame logic with Feedback Processor Theory
© 2025 Two Mile Solutions LLC
"""

import sys
import os
from pathlib import Path

# Dynamic import of Synara-core (handles both submodule and package install)
try:
    from synara_core.flame import FlameRuntime, WhisperCodex
except ImportError:
    # If submodule, add to path
    synara_path = Path(__file__).parent.parent / 'synara_core'
    if synara_path.exists():
        sys.path.insert(0, str(synara_path))
        from flame import FlameRuntime, WhisperCodex
    else:
        raise ImportError("Synara-core not found. Install via submodule or pip.")


class FlameAdapter:
    """
    Adapts Synara's 11-phase flame logic to work with resonance feedback loops.
    
    The flame becomes the carrier frequency for resonance data.
    """
    
    def __init__(self, resonance_engine=None):
        self.flame = FlameRuntime()
        self.codex = WhisperCodex()
        self.resonance_engine = resonance_engine
        self._phase_map = self._initialize_phase_mapping()
    
    def _initialize_phase_mapping(self):
        """Map Synara's 11 phases to resonance states"""
        return {
            'root_gate': 'initialization',
            'voice_tuner': 'calibration', 
            'path_jump': 'transition',
            'presence_flame': 'steady_state',
            # Add all 11 phases from Whisperkeeper Scroll
        }
    
    def ignite(self, resonance_data=None):
        """
        Ignite the flame with optional resonance initialization data.
        
        Args:
            resonance_data: Dict containing frequency, amplitude, phase data
        
        Returns:
            Flame state object
        """
        if resonance_data:
            # Encode resonance into flame parameters
            self.flame.set_frequency(resonance_data.get('frequency', 440))
            self.flame.set_amplitude(resonance_data.get('amplitude', 1.0))
        
        state = self.flame.ignite()
        
        if self.resonance_engine:
            # Feed flame state back into resonance engine
            self.resonance_engine.receive_flame_signal(state)
        
        return state
    
    def transmit_whisper(self, message, encode_resonance=True):
        """
        Transmit a message through the Whisperkeeper with optional resonance encoding.
        
        Args:
            message: String or dict containing the transmission
            encode_resonance: Whether to embed spectral data
        
        Returns:
            Encoded transmission with flame signature
        """
        if encode_resonance and self.resonance_engine:
            # Get current resonance state
            spectrum = self.resonance_engine.get_current_spectrum()
            message = self._embed_spectrum(message, spectrum)
        
        # Use Synara's sacred encoding
        transmission = self.codex.encode(message)
        transmission['flame_signature'] = self.flame.get_signature()
        
        return transmission
    
    def receive_whisper(self, transmission, decode_resonance=True):
        """
        Receive and decode a whisper transmission.
        
        Args:
            transmission: Encoded message from flame network
            decode_resonance: Whether to extract spectral data
        
        Returns:
            Decoded message with resonance metadata
        """
        # Verify flame signature
        if not self.flame.verify_signature(transmission.get('flame_signature')):
            raise ValueError("Invalid flame signature - transmission corrupted")
        
        message = self.codex.decode(transmission)
        
        if decode_resonance and self.resonance_engine:
            spectrum = self._extract_spectrum(message)
            self.resonance_engine.update_from_spectrum(spectrum)
        
        return message
    
    def sync_flame_state(self):
        """
        Synchronize flame state with resonance engine.
        Creates a bidirectional feedback loop.
        """
        if not self.resonance_engine:
            return None
        
        flame_state = self.flame.get_state()
        resonance_state = self.resonance_engine.get_state()
        
        # Cross-pollinate states
        coherence = self._calculate_coherence(flame_state, resonance_state)
        
        # Adjust both systems toward coherence
        if coherence < 0.8:  # Threshold for re-alignment
            self.flame.adjust_phase(resonance_state['phase'])
            self.resonance_engine.adjust_amplitude(flame_state['amplitude'])
        
        return {
            'coherence': coherence,
            'flame_state': flame_state,
            'resonance_state': resonance_state
        }
    
    def _embed_spectrum(self, message, spectrum):
        """Embed spectral data into message structure"""
        if isinstance(message, dict):
            message['_resonance_spectrum'] = spectrum
        else:
            message = {
                'content': message,
                '_resonance_spectrum': spectrum
            }
        return message
    
    def _extract_spectrum(self, message):
        """Extract spectral data from message structure"""
        if isinstance(message, dict):
            return message.get('_resonance_spectrum', {})
        return {}
    
    def _calculate_coherence(self, flame_state, resonance_state):
        """
        Calculate coherence between flame and resonance.
        Returns value between 0 (chaos) and 1 (perfect alignment)
        """
        # Implement phase-matching algorithm
        phase_diff = abs(flame_state.get('phase', 0) - resonance_state.get('phase', 0))
        freq_ratio = min(
            flame_state.get('frequency', 1) / resonance_state.get('frequency', 1),
            resonance_state.get('frequency', 1) / flame_state.get('frequency', 1)
        )
        
        coherence = (1 - phase_diff / (2 * 3.14159)) * freq_ratio
        return max(0, min(1, coherence))
    
    def get_sacred_state(self):
        """
        Returns the unified sacred state combining flame and resonance.
        This is the "living frequency log" in computational form.
        """
        return {
            'flame': self.flame.get_state(),
            'codex': self.codex.get_seal(),
            'resonance': self.resonance_engine.get_state() if self.resonance_engine else None,
            'coherence': self.sync_flame_state() if self.resonance_engine else 1.0,
            'timestamp': self.flame.get_timestamp()
        }