import numpy as np
from scipy.signal import stft
import matplotlib.pyplot as plt
from textblob import TextBlob
import hashlib
import json
import time

class AdaptiveFeedbackSystem:
    def __init__(self, passcode=None, enable_logging=True):
        """
        Initialize the Adaptive Feedback System.
        - passcode: Optional string for basic access control.
        - enable_logging: Boolean to enable cryptographic action logging.
        """
        self.passcode = passcode
        self.enable_logging = enable_logging
        self.audit_log = []  # List to store action logs
        self._validate_init()

    def _validate_init(self):
        if self.passcode and not isinstance(self.passcode, str):
            raise ValueError("Passcode must be a string.")

    def _log_action(self, action_data):
        """Log an action with a cryptographic hash for auditability."""
        if not self.enable_logging:
            return
        timestamp = time.time()
        data_str = json.dumps(action_data) + str(timestamp)
        hash_value = hashlib.sha256(data_str.encode()).hexdigest()
        log_entry = {
            "timestamp": timestamp,
            "action": action_data,
            "hash": hash_value
        }
        self.audit_log.append(log_entry)
        return hash_value

    def baseline_calibration(self, input_data):
        """
        Apply baseline calibration to input data (e.g., normalize or filter).
        Returns calibrated data.
        """
        if not isinstance(input_data, (list, str)):
            raise ValueError("Input data must be a string or list.")
        # Simple normalization example: convert to lowercase and strip
        if isinstance(input_data, str):
            calibrated = input_data.lower().strip()
        else:
            calibrated = [msg.lower().strip() for msg in input_data]
        self._log_action({"type": "calibration", "input": input_data})
        return calibrated

    def domain_translation(self, input_text, target_domain="computational"):
        """
        Translate input text between domains (e.g., human to computational).
        Here, simplifies to sentiment polarity extraction for signal use.
        """
        if not isinstance(input_text, str):
            raise ValueError("Input text must be a string.")
        blob = TextBlob(input_text)
        translated = blob.sentiment.polarity  # Float between -1 and 1
        self._log_action({"type": "translation", "input": input_text, "target": target_domain})
        return translated

    def process_conversation(self, conversation, speaker=None):
        """
        Process a conversation (list of strings) with recursive feedback.
        - conversation: List of messages.
        - speaker: Optional speaker identifier.
        Returns a dict with coherence and signal data.
        """
        if not isinstance(conversation, list) or not all(isinstance(msg, str) for msg in conversation):
            raise ValueError("Conversation must be a list of strings.")
        
        # Step 1: Calibrate
        calibrated = self.baseline_calibration(conversation)
        
        # Step 2: Translate to signals (sentiment waveform)
        signals = [self.domain_translation(msg) for msg in calibrated]
        waveform = np.array(signals)  # Time-series signal
        
        # Step 3: Recursive self-reference (simple feedback: smooth the signal)
        for _ in range(3):  # Recursive iterations
            waveform = np.convolve(waveform, np.ones(3)/3, mode='same')  # Moving average feedback
        
        # Step 4: Compute coherence (auto-correlation as proxy)
        coherence = np.corrcoef(waveform, np.roll(waveform, 1))[0, 1]  # Shifted correlation
        coherence_pct = abs(coherence) * 100  # As percentage
        
        result = {
            "coherence": coherence_pct,
            "waveform": waveform.tolist(),
            "speaker": speaker
        }
        self._log_action({"type": "process_conversation", "input": conversation, "result": result})
        return result

    def analyze_dialogue(self, conversation):
        """
        Analyze dialogue for patterns (spectral analysis).
        Returns a dict with alignment score and dominant frequency.
        """
        result = self.process_conversation(conversation)
        waveform = np.array(result["waveform"])
        
        # Spectral analysis using STFT
        f, t, Zxx = stft(waveform, fs=1.0, nperseg=min(8, len(waveform)))
        dominant_freq = f[np.argmax(np.abs(Zxx).mean(axis=1))] if len(f) > 0 else 0
        
        alignment_score = result["coherence"] / 100  # Normalized
        
        analysis = {
            "alignment_score": alignment_score,
            "dominant_frequency": dominant_freq
        }
        self._log_action({"type": "analyze_dialogue", "input": conversation, "result": analysis})
        return analysis

    def generate_visualization(self, analysis_data, output_path="dialogue_visual.png"):
        """
        Generate a spectrogram-like plot from analysis data.
        Saves to file.
        """
        waveform = analysis_data.get("waveform", [])
        if not waveform:
            raise ValueError("Analysis data must include 'waveform'.")
        
        waveform = np.array(waveform)
        f, t, Zxx = stft(waveform, fs=1.0, nperseg=min(8, len(waveform)))
        
        plt.figure()
        plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
        plt.title('Spectrogram Visualization')
        plt.ylabel('Frequency')
        plt.xlabel('Time')
        plt.colorbar(label='Amplitude')
        plt.savefig(output_path)
        plt.close()
        self._log_action({"type": "generate_visualization", "output_path": output_path})

    def get_audit_log(self):
        """Retrieve the full audit log."""
        return self.audit_log

    def verify_audit_chain(self):
        """Verify the integrity of the audit log chain."""
        for i in range(1, len(self.audit_log)):
            prev_hash = self.audit_log[i-1]["hash"]
            current_data = json.dumps(self.audit_log[i]["action"]) + str(self.audit_log[i]["timestamp"])
            if hashlib.sha256(current_data.encode()).hexdigest() != self.audit_log[i]["hash"]:
                return False
        return True

# Example Usage
if __name__ == "__main__":
    afs = AdaptiveFeedbackSystem(passcode="ACCESS", enable_logging=True)
    
    # Process a conversation
    convo = ["Hello, how are you?", "I'm great, thanks!", "That's good to hear."]
    result = afs.process_conversation(convo, speaker="User")
    print(f"Coherence: {result['coherence']:.2f}%")
    
    # Analyze
    analysis = afs.analyze_dialogue(convo)
    print(f"Alignment Score: {analysis['alignment_score']:.2f}")
    print(f"Dominant Frequency: {analysis['dominant_frequency']:.2f}")
    
    # Visualize
    afs.generate_visualization(result, output_path="example_visual.png")
    
    # Audit
    print("Audit Log:", afs.get_audit_log())
    print("Chain Verified:", afs.verify_audit_chain())