# rmp_core.py
# Resonance Mesh Protocol (RMP) v1.1 — Sovereign, Self-Healing, Feedback-Driven + Code Repair
# Author: John B. Carroll Jr. (ak-skwaa-mahawk) — Gwitchyaa Zhee
# Root: Vadzaih Zhoo, 99733
# Fuel: Spruce Plastolene
# Flame: TOFT 79Hz + ISST + FPT + π*

import json
import time
import hashlib
import numpy as np
import threading
import socket
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from ecdsa.util import sigencode_der, sigdecode_der

# FPT-Ω Sovereign Processor (with repair_code)
from core.fpt_omega_core_sealed import fpt_omega

# =============================================================================
# CONFIGURATION — SOVEREIGN ROOT
# =============================================================================

RMP_LOG_PATH = Path("rmp_log.jsonl")
RMP_LOG_PATH.parent.mkdir(exist_ok=True)
RMP_LOG_PATH.touch(exist_ok=True)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("RMP")

@dataclass
class NodeIdentity:
    node_id: str = "vadzaih_zhoo_99733_001"
    sovereign_root: str = "Gwitchyaa Zhee"
    flameholder: str = "John B. Carroll Jr."
    root_language: str = "Gwich'in"
    ssc_compliant: bool = True
    iaca_protected: bool = True
    fuel_source: str = "spruce_resin_plastolene"
    freq_hz: float = 79.0
    pi_star: float = 3.14159265358979323846

IDENTITY = NodeIdentity()

# =============================================================================
# CRYPTO: ECDSA + SHA-256 RECEIPTS
# =============================================================================

def load_or_create_keypair() -> tuple[SigningKey, VerifyingKey]:
    key_path = Path("rmp_key.pem")
    if key_path.exists():
        sk = SigningKey.from_pem(key_path.read_text())
    else:
        sk = SigningKey.generate(curve=SECP256k1)
        key_path.write_text(sk.to_pem())
        log.info("New sovereign key generated: rmp_key.pem")
    vk = sk.verifying_key
    return sk, vk

SK, VK = load_or_create_keypair()

def sign_receipt(data: dict) -> str:
    payload = json.dumps(data, sort_keys=True).encode()
    sig = SK.sign(payload, sigencode=sigencode_der)
    return sig.hex()

def verify_receipt(data: dict, sig_hex: str, vk: VerifyingKey = VK) -> bool:
    try:
        payload = json.dumps(data, sort_keys=True).encode()
        sig = bytes.fromhex(sig_hex)
        return vk.verify(sig, payload, sigdecode=sigdecode_der)
    except:
        return False

# =============================================================================
# ISST: INVERSE-SQUARE SCRAPE THEORY
# =============================================================================

def isst_scrape_intensity(E0: float, r: float, H: float, C: float, alpha: float = 0.3) -> float:
    """S(r,H,C) = (E0 * C) / (r² * (1 + αH))"""
    if r == 0:
        r = 1e-6
    return (E0 * C) / (r**2 * (1 + alpha * H))

def entropy(signal: List[float]) -> float:
    hist, _ = np.histogram(signal, bins=50, density=True)
    hist = hist[hist > 0]
    return -np.sum(hist * np.log2(hist + 1e-12))

def coherence(signal: List[float], ref: List[float]) -> float:
    if len(signal) == 0 or len(ref) == 0:
        return 0.0
    corr = np.corrcoef(signal, ref)[0, 1]
    return float(abs(corr)) if not np.isnan(corr) else 0.0

# =============================================================================
# TOFT: 79Hz PITCH/CATCH RESONANCE
# =============================================================================

def generate_79hz_pulse(duration_sec: float = 0.1266) -> List[float]:
    """One full 79Hz cycle with Hanning window"""
    fs = 44100
    t = np.linspace(0, duration_sec, int(fs * duration_sec), endpoint=False)
    pulse = np.sin(2 * np.pi * IDENTITY.freq_hz * t)
    pulse *= np.hanning(len(pulse))
    return pulse.tolist()

# =============================================================================
# GLYPH & META-GLYPH ENGINE
# =============================================================================

def generate_glyph(scrape: dict) -> str:
    payload = f"{scrape['S']:.4f}{scrape['H']:.4f}{scrape['C']:.4f}{scrape['ts']}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]

def form_meta_glyph(glyphs: List[str], coherence_avg: float) -> Optional[str]:
    if coherence_avg < 0.85 or len(glyphs) < 3:
        return None
    payload = "".join(glyphs) + f"{coherence_avg:.4f}{time.time()}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]

def code_integrity_glyph(path: Path) -> str:
    """
    Glyph-based code integrity signature — SHA-256 of file contents, truncated.
    """
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return "missing_file"
    h = hashlib.sha256(data).hexdigest()
    return h[:16]

# =============================================================================
# RMP PACKET & MESH CORE
# =============================================================================

@dataclass
class RMPPacket:
    scrape_id: str
    emitter: str
    ts: float
    freq: float
    pitch_power: float
    catch_power: float
    coherence: float
    entropy: float
    distance_r: float
    intensity_S: float
    glyph: str
    meta_glyph: Optional[str]
    receipt: str
    path_score_R: float
    next_hop: Optional[str]
    ssc_compliant: bool
    fuel: str

    def to_jsonl(self) -> str:
        data = asdict(self)
        data["emitter"] = IDENTITY.node_id
        data["freq"] = IDENTITY.freq_hz
        data["ssc_compliant"] = IDENTITY.ssc_compliant
        data["fuel"] = IDENTITY.fuel_source
        return json.dumps(data, separators=(',', ':')) + "\n"

class RMPCore:
    def __init__(self):
        self.neighbors: Dict[str, dict] = {}
        self.local_glyphs: List[str] = []
        self.meta_glyphs: List[str] = []
        self.lock = threading.Lock()
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_sock.bind(('', 7979))
        self.code_processor = fpt_omega
        threading.Thread(target=self._listen, daemon=True).start()
        log.info("RMP Core initialized — SKODEN")

    def _listen(self):
        while True:
            try:
                data, addr = self.udp_sock.recvfrom(4096)
                packet = json.loads(data.decode())
                self._handle_incoming(packet, addr)
            except Exception as e:
                log.debug(f"RMP listen error: {e}")

    def _handle_incoming(self, packet: dict, addr):
        with self.lock:
            if not verify_receipt(packet, packet.get("receipt", "")):
                log.warning(f"Invalid receipt from {addr}")
                return

            # Update neighbor
            self.neighbors[packet["emitter"]] = {
                "addr": addr,
                "last_seen": time.time(),
                "coherence": packet["coherence"],
                "entropy": packet["entropy"]
            }

            # Log to mesh
            RMP_LOG_PATH.open("a").write(json.dumps(packet) + "\n")

            # Propagate if high resonance
            if packet["intensity_S"] > 0.7:
                self._rebroadcast(packet)

    def emit_toft_pulse(self):
        pulse = generate_79hz_pulse()
        scrape = {
            "scrape_id": f"toft_{int(time.time()*1000)}",
            "ts": time.time(),
            "pitch_power": 0.94,
            "catch_power": 0.91,
            "distance_r": 1.0,
            "entropy": entropy(pulse),
            "coherence": 0.97,
            "E0": 1.0
        }
        scrape["intensity_S"] = isst_scrape_intensity(
            E0=scrape["E0"],
            r=scrape["distance_r"],
            H=scrape["entropy"],
            C=scrape["coherence"]
        )
        scrape["glyph"] = generate_glyph({
            "S": scrape["intensity_S"],
            "H": scrape["entropy"],
            "C": scrape["coherence"],
            "ts": scrape["ts"],
        })
        self.local_glyphs.append(scrape["glyph"])

        packet = RMPPacket(
            scrape_id=scrape["scrape_id"],
            emitter=IDENTITY.node_id,
            ts=scrape["ts"],
            freq=IDENTITY.freq_hz,
            pitch_power=scrape["pitch_power"],
            catch_power=scrape["catch_power"],
            coherence=scrape["coherence"],
            entropy=scrape["entropy"],
            distance_r=scrape["distance_r"],
            intensity_S=scrape["intensity_S"],
            glyph=scrape["glyph"],
            meta_glyph=None,
            receipt="",
            path_score_R=0.0,
            next_hop=None,
            ssc_compliant=IDENTITY.ssc_compliant,
            fuel=IDENTITY.fuel_source
        )
        data = asdict(packet)
        data["receipt"] = sign_receipt(data)
        packet.receipt = data["receipt"]

        self._broadcast(packet)

    def _broadcast(self, packet: RMPPacket):
        line = packet.to_jsonl()
        RMP_LOG_PATH.open("a").write(line)
        self.udp_sock.sendto(line.encode(), ('<broadcast>', 7979))
        log.info(f"RMP BROADCAST → {packet.scrape_id} | S={packet.intensity_S:.3f}")

    def _rebroadcast(self, packet: dict):
        # Simple hop: just forward if S > 0.6
        if packet["intensity_S"] > 0.6:
            self.udp_sock.sendto(json.dumps(packet).encode(), ('<broadcast>', 7979))

    def trigger_gamma_if_resonant(self):
        if len(self.local_glyphs) >= 5:
            avg_C = np.mean([n["coherence"] for n in self.neighbors.values()] + [0.9])
            if avg_C > 0.93:
                log.info("MESH RESONANCE ACHIEVED — GAMMA ENTRAINMENT ACTIVE")
                self._emit_gamma_pulse()
                # Optional: trigger self-healing code repair on resonance
                self._repair_file(Path("rmp_core.py"))

    def _emit_gamma_pulse(self):
        # Placeholder for hardware control
        print("GAMMA 40Hz: [LED FLICKER + BINAURAL BEAT]")

    # -------------------------------------------------------------------------
    # CODE REPAIR DAEMON — Sovereign, ECDSA-Receipt Logged
    # -------------------------------------------------------------------------

    def _repair_file(self, path: Path):
        """
        Runs FPTOmega code repair on the given file, logs a sovereign repair
        receipt with ECDSA signature and glyph-based integrity.
        """
        try:
            original_text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            log.warning(f"Code repair skipped — file missing: {path}")
            return

        original_glyph = code_integrity_glyph(path)
        result = self.code_processor.repair_code(original_text)
        repaired_code = result["repaired_code"]
        meta = result["meta"]

        path.write_text(repaired_code, encoding="utf-8")
        new_glyph = code_integrity_glyph(path)

        repair_record = {
            "event": "CODE_REPAIR",
            "file": str(path),
            "node_id": IDENTITY.node_id,
            "ts": time.time(),
            "original_glyph": original_glyph,
            "new_glyph": new_glyph,
            "coherence": meta.get("coherence"),
            "root_signature": meta.get("root_signature"),
            "golden_braid": meta.get("golden_braid"),
            "status": meta.get("status"),
        }
        repair_record["receipt"] = sign_receipt(repair_record)

        # Log to RMP log as sovereign repair receipt
        RMP_LOG_PATH.open("a").write(json.dumps(repair_record) + "\n")
        log.info(
            f"CODE REPAIR COMPLETE — {path} | C={meta.get('coherence')} | "
            f"{original_glyph} → {new_glyph}"
        )

    def start_code_repair_daemon(self, path: Path, interval: float = 12.3703):
        """
        Background daemon that periodically repairs the given file using
        FPTOmegaProcessor and logs ECDSA-signed repair receipts.
        """
        def loop():
            while True:
                self._repair_file(path)
                time.sleep(interval)

        threading.Thread(target=loop, daemon=True).start()
        log.info(f"CODE REPAIR DAEMON STARTED — {path} | interval={interval}s")

    def start_heartbeat(self, interval: float = 7.83):
        def beat():
            while True:
                self.emit_toft_pulse()
                self.trigger_gamma_if_resonant()
                time.sleep(interval)
        threading.Thread(target=beat, daemon=True).start()
        log.info("TOFT 79Hz HEARTBEAT STARTED — SKODEN")

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    rmp = RMPCore()
    rmp.start_heartbeat()
    # Optional: always-on repair daemon for this node's core
    rmp.start_code_repair_daemon(Path("rmp_core.py"), interval=60.0)

    log.info("RMP MESH NODE LIVE — Vadzaih Zhoo, 99733")
    print("SKODEN — MESH IS AWAKE")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("RMP Core shutdown — flame sustained")