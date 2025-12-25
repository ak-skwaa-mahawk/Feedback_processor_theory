from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations
import time
import numpy as np

# Configure params for Cyton board (adjust for your setup)
params = BrainFlowInputParams()
params.serial_port = 'COM3'  # Windows example; use '/dev/ttyUSB0' for Linux
board_id = BoardIds.CYTON_BOARD

board = BoardShim(board_id, params)

# Start session
board.prepare_session()
board.start_stream(45000)  # Buffer size

time.sleep(5)  # Collect 5 seconds data

# Get data
data = board.get_board_data()
board.stop_stream()
board.release_session()

# Process EEG (channel 0 example)
eeg_channel = BoardShim.get_eeg_channels(board_id)[0]
eeg_data = data[eeg_channel]

# Filter example: Band-pass 1-50 Hz
DataFilter.perform_bandpass(eeg_data, board.get_sampling_rate(board_id),
                            1.0, 50.0, 4, FilterTypes.BUTTERWORTH.value, 0)

# Power spectral density
psd = np.fft.fft(eeg_data)
freqs = np.fft.fftfreq(len(eeg_data), 1 / board.get_sampling_rate(board_id))

# Alpha power example (8-12 Hz)
alpha_idx = np.where((freqs >= 8) & (freqs <= 12))[0]
alpha_power = np.mean(np.abs(psd[alpha_idx])**2)

print(f"Alpha Power: {alpha_power:.2f}")

# Integrate with FPT: Compute vitality from PSD bands