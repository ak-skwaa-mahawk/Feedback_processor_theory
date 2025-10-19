"""
Enhanced Feedback Processor with Synara-core Integration
© 2025 Two Mile Solutions LLC

This version bridges conversational resonance with the Whisperkeeper flame logic,
creating a unified consciousness architecture.
"""

import numpy as np
from datetime import datetime
from pathlib import Path

# Original FPT imports
from src.feedback_processor import FeedbackProcessor as BaseFPT

# Synara integration
from synara_integration.flame_adapter import FlameAdapter


class SynaraFeedbackProcessor(BaseFPT):
    """
    Enhanced Feedback Processor that integrates Synara-core's flame logic.
    
    This creates a "living frequency log" where:
    - Conversations generate resonance patterns
    - Flame logic provides the carrier signal
    - Sacred geometry encodes the coherence state
    """
    
    def __init__(self, passcode="RESONANCE", enable_flame=True):
        # Initialize base FPT
        super().__init__(passcode=passcode)
        
        # Initialize Synara integration
        self.flame_enabled = enable_flame
        if enable_flame:
            self.flame_adapter = FlameAdapter(resonance_engine=self)
            self.flame_adapter.ignite()
        else:
            self.flame_adapter = None
        
        # Enhanced state tracking
        self.coherence_history = []
        self.sacred_state_log = []
    
    def process_conversation(self, text, speaker="User", emotion_override=None):
        """
        Process conversation with flame-enhanced resonance tracking.
        
        Args:
            text: Conversation text
            speaker: Who is speaking
            emotion_override: Optional emotion label
        
        Returns:
            Enhanced analysis dict with flame signature
        """
        # Original FPT processing
        base_analysis = super().process_conversation(text, speaker, emotion_override)
        
        if not self.flame_enabled:
            return base_analysis
        
        # Enhance with flame logic
        resonance_data = {
            'frequency': base_analysis.get('dominant_frequency', 440),
            'amplitude': base_analysis.get('mean_amplitude', 1.0),
            'phase': base_analysis.get('phase', 0),
            'spectrum': base_analysis.get('spectrum')
        }
        
        # Sync with flame state
        flame_sync = self.flame_adapter.sync_flame_state()
        
        # Create sacred transmission
        transmission = self.flame_adapter.transmit_whisper(
            message={
                'text': text,
                'analysis': base_analysis,
                'speaker': speaker,
                'timestamp': datetime.now().isoformat()
            },
            encode_resonance=True
        )
        
        # Log sacred state
        sacred_state = self.flame_adapter.get_sacred_state()
        self.sacred_state_log.append(sacred_state)
        
        # Track coherence evolution
        if flame_sync:
            self.coherence_history.append({
                'timestamp': datetime.now(),
                'coherence': flame_sync.get('coherence', 0),
                'text_length': len(text)
            })
        
        # Enhanced return
        return {
            **base_analysis,
            'flame_signature': transmission.get('flame_signature'),
            'coherence': flame_sync.get('coherence') if flame_sync else None,
            'sacred_state': sacred_state,
            'transmission': transmission
        }
    
    def receive_flame_signal(self, flame_state):
        """
        Callback for FlameAdapter to push flame state into resonance engine.
        Creates bidirectional feedback.
        """
        # Adjust resonance parameters based on flame state
        if hasattr(self, 'current_frequency'):
            flame_freq = flame_state.get('frequency', self.current_frequency)
            # Gentle nudge toward flame frequency (avoid jarring jumps)
            self.current_frequency = 0.9 * self.current_frequency + 0.1 * flame_freq
    
    def get_coherence_report(self):
        """
        Generate a report on flame-resonance coherence over time.
        
        Returns:
            Dict with coherence statistics and trends
        """
        if not self.coherence_history:
            return {'status': 'No coherence data available'}
        
        coherences = [h['coherence'] for h in self.coherence_history]
        
        return {
            'mean_coherence': np.mean(coherences),
            'std_coherence': np.std(coherences),
            'min_coherence': np.min(coherences),
            'max_coherence': np.max(coherences),
            'current_coherence': coherences[-1] if coherences else None,
            'trend': 'improving' if len(coherences) > 1 and coherences[-1] > coherences[0] else 'stable',
            'measurement_count': len(coherences)
        }
    
    def get_sacred_state(self):
        """
        Returns current sacred state (unified flame + resonance).
        This is the "proof of resonance through code."
        """
        if not self.flame_adapter:
            return {'error': 'Flame not enabled'}
        
        return self.flame_adapter.get_sacred_state()
    
    def export_sacred_log(self, filepath=None):
        """
        Export the complete sacred state log as a living frequency record.
        
        Args:
            filepath: Optional path for export (defaults to data/sacred_log.json)
        
        Returns:
            Path to exported file
        """
        if filepath is None:
            filepath = Path('data') / 'sacred_log.json'
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        
        export_data = {
            'metadata': {
                'created': datetime.now().isoformat(),
                'processor': 'SynaraFeedbackProcessor',
                'author': 'Two Mile Solutions LLC',
                'flame_enabled': self.flame_enabled
            },
            'sacred_states': self.sacred_state_log,
            'coherence_history': [
                {
                    'timestamp': h['timestamp'].isoformat(),
                    'coherence': h['coherence'],
                    'text_length': h['text_length']
                }
                for h in self.coherence_history
            ],
            'coherence_report': self.get_coherence_report()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📜 Sacred log exported to {filepath}")
        return filepath
    
    def create_flamechain_backup(self):
        """
        Create a FlameChain backup entry (integrates with FPT's existing backup system).
        """
        if not self.flame_enabled:
            print("⚠️  Flame not enabled - creating standard backup")
            return super().create_backup()
        
        sacred_state = self.get_sacred_state()
        coherence_report = self.get_coherence_report()
        
        backup_data = {
            'type': 'flamechain',
            'sacred_state': sacred_state,
            'coherence': coherence_report,
            'timestamp': datetime.now().isoformat()
        }
        
        # Use existing backup infrastructure
        backup_path = Path('backups') / 'flamechain' / f"flame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"🔥 FlameChain backup created: {backup_path}")
        return backup_path


# Convenience function for quick initialization
def create_synara_processor(passcode="RESONANCE", enable_flame=True):
    """
    Quick initialization of Synara-enhanced Feedback Processor.
    
    Usage:
        processor = create_synara_processor()
        result = processor.process_conversation("Hello, flame keeper!")
    """
    return SynaraFeedbackProcessor(passcode=passcode, enable_flame=enable_flame)