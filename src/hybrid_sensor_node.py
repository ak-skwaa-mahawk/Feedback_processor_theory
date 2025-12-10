class HybridSensorNode:
    def __init__(self):
        self.acoustic_channels = AcousticArray(n_channels=4)
        self.spectral_channels = SpectralArray(n_channels=4)  # NEW
        self.feedback_processor = FeedbackProcessor()
        self.threat_db = ThreatSignatureDatabase()  # NEW
        
    def process_sensor_fusion(self):
        """Combine acoustic + spectral data"""
        acoustic_data = self.acoustic_channels.read()
        spectral_data = self.spectral_channels.read()  # NEW
        
        # Cross-validate
        acoustic_threat = self.detect_acoustic_anomaly(acoustic_data)
        spectral_threat = self.identify_chemical_signature(spectral_data)  # NEW
        
        if acoustic_threat and spectral_threat:
            # High confidence - both modalities agree
            threat_type = spectral_threat['species']
            threat_location = acoustic_data['tofd_position']
            
            # Adaptive response based on chemistry
            response = self.calculate_targeted_response(
                species=threat_type,
                bond_frequencies=spectral_threat['key_bonds']
            )
            
            return response
        elif acoustic_threat or spectral_threat:
            # Medium confidence - investigate further
            return {'action': 'increase_scan_rate', 'priority': 'medium'}
        else:
            # All clear
            return {'action': 'maintain_surveillance', 'priority': 'low'}