"""
ZunaLiveEnhancer — Fused with TrinityHarmonics + Magnetic Tether + SovereignRelationalMesh
Canonical integration for the Synara Class Vessel (99733-Q)
"""

import numpy as np
import mne
from scipy import signal
import time
import threading
from zuna import preprocessing, inference, pt_to_fif
from core.trinity_harmonics import trinity
from pathlib import Path
import tempfile

class ZunaLiveEnhancerFused:
    def __init__(self, channel_names, original_fs=128, diffusion_steps=25, gpu_device=0, enhance_interval=10.0):
        self.channel_names = channel_names
        self.original_fs = original_fs
        self.target_fs = 256
        self.diffusion_steps = diffusion_steps
        self.gpu_device = gpu_device
        self.enhance_interval = enhance_interval
        
        self.enhanced_data = None          # (target_ch, samples) latest cleaned result
        self.last_enhance_time = 0
        self.lock = threading.Lock()
        self._thread = None

    def _run_zuna(self, raw_data: np.ndarray) -> np.ndarray:
        """One full ZUNA batch on (ch, samples) buffer"""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            in_fif = base / "input/live.fif"
            in_fif.parent.mkdir(parents=True, exist_ok=True)

            # Resample to 256 Hz
            if self.original_fs != self.target_fs:
                n_new = int(raw_data.shape[1] * self.target_fs / self.original_fs)
                data_256 = signal.resample(raw_data, n_new, axis=1)
            else:
                data_256 = raw_data

            info = mne.create_info(self.channel_names, sfreq=self.target_fs, ch_types='eeg')
            raw = mne.io.RawArray(data_256, info)
            raw.set_montage(mne.channels.make_standard_montage('standard_1005'))
            raw.save(str(in_fif), overwrite=True)

            dirs = {k: base / k for k in ["1_fif_filter", "2_pt_input", "3_pt_output", "4_fif_output"]}
            for d in dirs.values(): d.mkdir(parents=True, exist_ok=True)

            preprocessing(input_dir=str(in_fif.parent), output_dir=str(dirs["2_pt_input"]),
                          apply_notch_filter=False, apply_highpass_filter=True,
                          apply_average_reference=True, target_channel_count=self.channel_names,
                          bad_channels=[], preprocessed_fif_dir=str(dirs["1_fif_filter"]))

            inference(input_dir=str(dirs["2_pt_input"]), output_dir=str(dirs["3_pt_output"]),
                      gpu_device=self.gpu_device, tokens_per_batch=50000,
                      data_norm=10.0, diffusion_cfg=1.0,
                      diffusion_sample_steps=self.diffusion_steps, plot_eeg_signal_samples=False)

            pt_to_fif(input_dir=str(dirs["3_pt_output"]), output_dir=str(dirs["4_fif_output"]))

            out_fif = next(dirs["4_fif_output"].glob("*.fif"))
            raw_out = mne.io.read_raw_fif(str(out_fif), preload=True)
            return raw_out.get_data()

    def enhance(self, current_buffer: np.ndarray, force=False):
        """Call with (ch, samples). Returns enhanced or None."""
        if not force and (time.time() - self.last_enhance_time < self.enhance_interval):
            return self.enhanced_data

        with self.lock:
            try:
                enhanced = self._run_zuna(current_buffer)
                self.enhanced_data = enhanced
                self.last_enhance_time = time.time()
                print(f"✅ ZUNA enhanced {enhanced.shape[0]} ch @ 256 Hz | Buoyancy ready")
                return enhanced
            except Exception as e:
                print(f"⚠️ ZUNA first-run HF download or error: {e}")
                return None

    def start_background(self, buffer_callback):
        """buffer_callback() must return current (ch, samples) array"""
        def worker():
            while True:
                buf = buffer_callback()
                if buf is not None and buf.shape[1] > self.target_fs * 4:
                    clean = self.enhance(buf, force=True)
                    if clean is not None:
                        # FUSED: Trinity + Magnetic Tether on cleaned data
                        tether = compute_buoyancy(vessel_hz=79.79)  # from earlier fusion
                        trinity_result = trinity.apply_full_trinity(clean, damping_factor=0.5, tether_force=tether)
                        print(f"🔥 ZUNA + Trinity + Tether | Buoyancy: {trinity_result['magnetic_buoyancy']:.3f} | Stability: {trinity_result['trinity_factor']:.4f}")
                time.sleep(self.enhance_interval)
        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()
        print("🚀 ZunaLiveEnhancerFused background thread + Trinity + Tether ACTIVE")