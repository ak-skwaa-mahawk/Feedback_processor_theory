import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations
import time

class OpenBCIIntegrator:
    def __init__(self, board_type=BoardIds.CYTON_BOARD, serial_port=None):
        params = BrainFlowInputParams()
        params.serial_port = serial_port  # e.g., 'COM3' Windows, '/dev/ttyUSB0' Linux
        self.board_id = board_type
        self.board = BoardShim(self.board_id, params)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.eeg_channels = BoardShim.get_eeg_channels(self.board_id)

    def start_session(self):
        self.board.prepare_session()
        self.board.start_stream()

    def get_latest_samples(self, num_samples=256):
        data = self.board.get_board_data(num_samples)
        eeg_data = data[self.eeg_channels]  # Shape: (channels, samples)
        return eeg_data

    def stop_session(self):
        self.board.stop_stream()
        self.board.release_session()

# --- Tie into FPT MeshNode (Example Extension) ---
# In MeshNode.update_from_biofeedback():
def integrate_openbci(self, integrator, channel=0):
    """Use real OpenBCI data instead of simulation."""
    eeg_data = integrator.get_latest_samples()
    if eeg_data.size > 0:
        channel_data = eeg_data[channel]  # Single channel for simplicity
        # Feed to band power/HRV calc (replace simulate)
        self.raw_buffer.extend(channel_data[-self.fs*2:])  # Fill buffer

# --- Demo Usage ---
if __name__ == "__main__":
    # Example for Cyton USB
    integrator = OpenBCIIntegrator(board_type=BoardIds.CYTON_BOARD, serial_port='COM3')  # Adjust port
    integrator.start_session()
    
    node = MeshNode("OpenBCI_Node")
    try:
        for _ in range(50):
            node.integrate_openbci(integrator)
            node.calculate_vitality_from_bands()
            time.sleep(0.1)
    finally:
        integrator.stop_session()