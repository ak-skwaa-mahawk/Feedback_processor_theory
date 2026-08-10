import numpy as np
import mne
from scipy import signal
import tempfile
from pathlib import Path
import time
import threading
from zuna import preprocessing, inference, pt_to_fif

class ZunaLiveEnhancerFused:
    def __init__(self, channel_names, original_fs=128,
                 target_channel_names=None,
                 diffusion_steps=20,
                 gpu_device=0,
                 enhance_interval=12.0):
        """
        Fused live enhancer for your MeshNode ecosystem.
        """
        self.channel_names = channel_names
        self.original_fs = original_fs
        self.target_fs = 256
        self.target_channel_names = target_channel_names or channel_names
        self.diffusion_steps = diffusion_steps
        self.gpu_device = gpu_device if gpu_device is not None else ""
        self.enhance_interval = enhance_interval

        self.montage = mne.channels.make_standard_montage('standard_1005')
        self.enhanced_data = None          # (target_ch, samples) — latest fused output
        self.last_enhance_time = 0
        self.lock = threading.Lock()
        self._thread = None

        print(f"🔗 ZunaLiveEnhancerFused ready → {len(self.channel_names)}→{len(self.target_channel_names)} channels @ {self.target_fs} Hz")

    def _buffer_to_fif(self, data: np.ndarray, tmp_base: Path):
        """Convert live buffer → single .fif with montage"""
        if self.original_fs != self.target_fs:
            n_new = int(data.shape[1] * self.target_fs / self.original_fs)
            data = signal.resample(data, n_new, axis=1)

        info = mne.create_info(self.channel_names, sfreq=self.target_fs, ch_types='eeg')
        raw = mne.io.RawArray(data, info)
        raw.set_montage(self.montage, on_missing='ignore')
        fif_path = tmp_base / "live_input.fif"
        raw.save(str(fif_path), overwrite=True)
        return fif_path

    def _run_zuna_fusion(self, raw_data: np.ndarray):
        """Core pipeline: buffer → ZUNA → enhanced .fif → numpy"""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            dirs = {k: base / k for k in ["1_fif_filter", "2_pt_input", "3_pt_output", "4_fif_output"]}
            for d in dirs.values():
                d.mkdir(parents=True, exist_ok=True)

            input_fif = self._buffer_to_fif(raw_data, base)

            # === PREPROCESSING ===
            preprocessing(
                input_dir=str(base),
                output_dir=str(dirs["2_pt_input"]),
                apply_notch_filter=False,
                apply_highpass_filter=True,
                apply_average_reference=True,
                target_channel_count=self.target_channel_names,   # ← this is the magic for spatial fill
                bad_channels=[],
                preprocessed_fif_dir=str(dirs["1_fif_filter"]),
            )

            # === INFERENCE ===
            inference(
                input_dir=str(dirs["2_pt_input"]),
                output_dir=str(dirs["3_pt_output"]),
                gpu_device=self.gpu_device,
                tokens_per_batch=50000,
                data_norm=10.0,
                diffusion_cfg=1.0,
                diffusion_sample_steps=self.diffusion_steps,
                plot_eeg_signal_samples=False,
            )

            # === PT → FIF ===
            pt_to_fif(
                input_dir=str(dirs["3_pt_output"]),
                output_dir=str(dirs["4_fif_output"]),
            )

            # Load final result
            out_fif = next(dirs["4_fif_output"].glob("*.fif"))
            raw_out = mne.io.read_raw_fif(str(out_fif), preload=True, verbose=False)
            return raw_out.get_data()  # (target_channels, samples)

    def enhance(self, current_buffer: np.ndarray, force=False):
        """Call this with your latest (ch, samples) buffer"""
        if not force and (time.time() - self.last_enhance_time < self.enhance_interval):
            return self.enhanced_data

        with self.lock:
            try:
                enhanced = self._run_zuna_fusion(current_buffer)
                self.enhanced_data = enhanced
                self.last_enhance_time = time.time()
                print(f"🌊 ZUNA fused → {enhanced.shape[0]}ch @ {self.target_fs}Hz (every {self.enhance_interval}s)")
                return enhanced
            except Exception as e:
                print(f"⚠️ ZUNA fusion error (first run downloads \~1.2 GB model): {e}")
                return None

    def start_background(self, buffer_callback):
        """buffer_callback() must return current (ch, samples) numpy array"""
        def worker():
            while True:
                buf = buffer_callback()
                if buf is not None and buf.shape[1] >= self.target_fs * 5:  # at least one full epoch
                    self.enhance(buf, force=True)
                time.sleep(self.enhance_interval)
        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()
        print("🚀 ZunaLiveEnhancerFused background thread LIVE — mesh now breathes with foundation priors")