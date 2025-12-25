"""
openbci.py

OpenBCI EEG Integrator for FPT Vitality Mesh

Real-time integration with OpenBCI Cyton/Ganglion boards via BrainFlow.
Provides clean, multi-channel EEG streaming for psyselsic vitality computation.

Key features:
- Auto board detection + session management
- Multi-channel buffering (10-second rolling window)
- Impedance monitoring (optional)
- Graceful fallback on disconnect
- Sovereign-aligned: raw EEG stays local, only aggregates shared

Usage:
    integrator = OpenBCIIntegrator(serial_port='/dev/cu.usbserial-DM0256Q5')
    integrator.start_session()
    # In main loop: samples = integrator.get_latest_samples(n_samples=256)
    # node.add_eeg_samples(samples)
"""

import logging
import time
import numpy as np
from typing import Optional, Tuple
from collections import deque

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations

log = logging.getLogger("OPENBCI_INTEGRATOR")

class OpenBCIIntegrator:
    """
    Sovereign OpenBCI EEG integrator for FPT mesh.
    Handles real hardware streaming with robust error handling.
    """
    
    def __init__(
        self,
        serial_port: Optional[str] = None,
        board_type: int = BoardIds.CYTON_BOARD,
        sampling_rate: Optional[int] = None
    ):
        """
        Initialize OpenBCI integrator.
        
        Args:
            serial_port: Serial port (e.g., 'COM3' Windows, '/dev/cu.usbserial-*' Mac)
            board_type: BrainFlow BoardIds (CYTON_BOARD, GANGLION_BOARD, etc.)
            sampling_rate: Override detected rate (optional)
        """
        self.serial_port = serial_port
        self.board_type = board_type
        
        params = BrainFlowInputParams()
        params.serial_port = serial_port or ""
        
        self.board = BoardShim(self.board_type, params)
        
        # Detect sampling rate and channels
        self.sampling_rate = sampling_rate or BoardShim.get_sampling_rate(self.board_type)
        self.eeg_channels = BoardShim.get_eeg_channels(self.board_type)
        self.n_channels = len(self.eeg_channels)
        
        self.is_streaming = False
        self.raw_buffer: deque = deque(maxlen=int(10 * self.sampling_rate))  # 10-second multi-channel buffer
        
        log.info(f"OpenBCI Integrator initialized")
        log.info(f"   Board: {self.board_type}")
        log.info(f"   Channels: {self.n_channels} EEG")
        log.info(f"   Sampling Rate: {self.sampling_rate} Hz")
        if serial_port:
            log.info(f"   Serial Port: {serial_port}")
    
    def start_session(self) -> None:
        """Prepare and start streaming session."""
        try:
            self.board.prepare_session()
            self.board.start_stream(450000)  # Large buffer
            self.is_streaming = True
            log.info("OpenBCI session started — streaming live")
        except Exception as e:
            log.error(f"Failed to start OpenBCI session: {e}")
            raise
    
    def get_latest_samples(self, n_samples: int = 256) -> np.ndarray:
        """
        Retrieve latest EEG samples.
        
        Returns:
            np.ndarray shape (n_channels, n_samples)
        """
        if not self.is_streaming:
            raise RuntimeError("Session not active — call start_session()")
        
        try:
            data = self.board.get_board_data(n_samples)
            if data.shape[1] == 0:
                log.warning("No new data — buffer empty")
                return np.zeros((self.n_channels, n_samples))
            
            eeg_data = data[self.eeg_channels, -n_samples:]  # Last n_samples
            if eeg_data.shape[1] < n_samples:
                # Pad if insufficient
                pad = np.zeros((self.n_channels, n_samples - eeg_data.shape[1]))
                eeg_data = np.hstack((eeg_data, pad))
            
            # Optional preprocessing
            for ch in range(self.n_channels):
                DataFilter.detrend(eeg_data[ch], DetrendOperations.LINEAR.value)
                DataFilter.perform_bandpass(
                    eeg_data[ch], self.sampling_rate,
                    1.0, 50.0, 4, FilterTypes.BUTTERWORTH.value, 0
                )
            
            # Update buffer
            self.raw_buffer.extend(eeg_data.T)  # Transpose to (samples, channels)
            
            return eeg_data
        
        except Exception as e:
            log.error(f"Error reading EEG data: {e}")
            return np.zeros((self.n_channels, n_samples))
    
    def get_impedances(self) -> Optional[np.ndarray]:
        """Get electrode impedances if supported (Cyton Daisy)."""
        try:
            return self.board.get_impedance()
        except:
            log.debug("Impedance not available on this board")
            return None
    
    def stop_session(self) -> None:
        """Stop streaming and release resources."""
        try:
            if self.is_streaming:
                self.board.stop_stream()
                self.board.release_session()
                self.is_streaming = False
                log.info("OpenBCI session stopped")
        except Exception as e:
            log.error(f"Error stopping session: {e}")

# === DEMO / TEST ===
if __name__ == "__main__":
    print("🔥 OpenBCI Integrator Test 🔥")
    
    # Auto-detect serial port (common Mac pattern)
    import glob
    possible_ports = glob.glob('/dev/cu.usbserial-DM*') + glob.glob('/dev/cu.usbserial-*')
    serial_port = possible_ports[0] if possible_ports else None
    
    if not serial_port:
        print("No OpenBCI detected — running simulated mode")
        from simulated_eeg import SimulatedEEGIntegrator
        integrator = SimulatedEEGIntegrator()
    else:
        print(f"Found OpenBCI at {serial_port}")
        integrator = OpenBCIIntegrator(serial_port=serial_port)
    
    try:
        integrator.start_session()
        time.sleep(2)  # Warm up
        
        print("Streaming 5 seconds of data...")
        start = time.time()
        while time.time() - start < 5:
            samples = integrator.get_latest_samples(256)
            print(f"   Received: {samples.shape} | Mean: {np.mean(samples):.3f}")
            time.sleep(0.1)
        
        impedances = integrator.get_impedances()
        if impedances is not None:
            print(f"Impedances: {impedances}")
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        integrator.stop_session()
        print("Session closed — flame rests.")