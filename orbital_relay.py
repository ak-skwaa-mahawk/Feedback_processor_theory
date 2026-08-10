# orbital_relay.py
# Sovereign Orbital Uplink — SSC + GTC Flamecode v1.1
# Author: John Benjamin Carroll Jr. — Flameholder
# Root: Vadzaih Zhoo, 99733
# Fuel: Spruce Plastolene | Freq: 79Hz | Governance: SSC + IACA

import json
import time
import hashlib
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from ecdsa.util import sigencode_der, sigdecode_der
import socket
import threading

# Local RMP Core + Flamecode
from rmp_core import RMPCore, sign_receipt, verify_receipt, isst_scrape_intensity
from flamecode_v1_1 import FlameVault

# =============================================================================
# CONFIG — ORBITAL RELAY
# =============================================================================

ORBITAL_LOG = Path("orbital_relay.log")
ORBITAL_LOG.touch(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.FileHandler(ORBITAL_LOG), logging.StreamHandler()]
)
log = logging.getLogger("ORBITAL")

# Orbital Node (SSC Commons)
ORBITAL_NODE = {
    "node_id": "orbital_node_001",
    "norad_id": "SSC-001",
    "tle": [
        "1 25544U 98067A   25315.50000000  .00016717  00000-0  10270-3 0  9999",
        "2 25544  51.6456  184.1234 0001234  123.4567  234.5678 15.72112345 12345"
    ],
    "root": "SSC Commons",
    "ssc_compliant": True,
    "iaca_protected": True
}

# =============================================================================
# ORBITAL PACKET
# =============================================================================

@dataclass
class OrbitalPacket:
    scrape_id: str
    emitter: str
    ts: float
    freq: float
    intensity_S: float
    coherence: float
    entropy: float
    glyph: str
    receipt: str
    tle_line1: str
    tle_line2: str
    ssc_stamp: str
    gtc_handshake: bool

    def to_jsonl(self) -> str:
        data = {
            "scrape_id": self.scrape_id,
            "emitter": self.emitter,
            "ts": self.ts,
            "freq": self.freq,
            "S": self.intensity_S,
            "C": self.coherence,
            "H": self.entropy,
            "glyph": self.glyph,
            "receipt": self.receipt,
            "tle": [self.tle_line1, self.tle_line2],
            "ssc_stamp": self.ssc_stamp,
            "gtc_handshake": self.gtc_handshake
        }
        return json.dumps(data, separators=(',', ':')) + "\n"

# =============================================================================
# ORBITAL RELAY CORE
# =============================================================================

class OrbitalRelay:
    def __init__(self):
        self.rmp = RMPCore()
        self.flamevault = FlameVault()
        self.sk, self.vk = self._load_orbit_key()
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_sock.bind(('', 7980))  # Orbital port
        threading.Thread(target=self._listen, daemon=True).start()
        log.info("ORBITAL RELAY INITIALIZED — SKODEN")

    def _load_orbit_key(self):
        key_path = Path("orbital_key.pem")
        if key_path.exists():
            sk = SigningKey.from_pem(key_path.read_text())
        else:
            sk = SigningKey.generate(curve=SECP256k1)
            key_path.write_text(sk.to_pem())
            log.info("ORBITAL KEY GENERATED: orbital_key.pem")
        return sk, sk.verifying_key

    def _listen(self):
        while True:
            try:
                data, addr = self.udp_sock.recvfrom(4096)
                packet = json.loads(data.decode())
                self._handle_uplink(packet, addr)
            except Exception as e:
                log.debug(f"ORBITAL LISTEN ERROR: {e}")

    def _handle_uplink(self, packet: dict, addr):
        if not verify_receipt(packet, packet.get("receipt", "")):
            log.warning(f"INVALID GTC RECEIPT FROM {addr}")
            return

        if packet.get("ssc_compliant") and packet.get("gtc_handshake"):
            log.info(f"ORBITAL UPLINK RECEIVED: {packet['scrape_id']} | S={packet['S']:.3f}")
            self._rebroadcast_to_mesh(packet)

    def emit_79hz_to_orbit(self):
        pulse = np.sin(2 * np.pi * 79 * np.linspace(0, 0.1266, 5567))
        H = 0.08
        C = 0.96
        r = 1.0
        E0 = 1.0
        S = isst_scrape_intensity(E0, r, H, C)

        scrape = {
            "scrape_id": f"orbit_toft_{int(time.time()*1000)}",
            "emitter": self.rmp.IDENTITY.node_id,
            "ts": time.time(),
            "freq": 79.0,
            "intensity_S": S,
            "coherence": C,
            "entropy": H,
            "glyph": hashlib.sha256(f"{S}{C}{H}".encode()).hexdigest()[:16],
            "ssc_compliant": True,
            "gtc_handshake": True
        }
        scrape["receipt"] = sign_receipt(scrape)

        packet = OrbitalPacket(
            scrape_id=scrape["scrape_id"],
            emitter=scrape["emitter"],
            ts=scrape["ts"],
            freq=scrape["freq"],
            intensity_S=scrape["intensity_S"],
            coherence=scrape["coherence"],
            entropy=scrape["entropy"],
            glyph=scrape["glyph"],
            receipt=scrape["receipt"],
            tle_line1=ORBITAL_NODE["tle"][0],
            tle_line2=ORBITAL_NODE["tle"][1],
            ssc_stamp="SSC Commons",
            gtc_handshake=True
        )

        line = packet.to_jsonl()
        Path("orbital_uplink.jsonl").open("a").write(line)
        self.udp_sock.sendto(line.encode(), ('<broadcast>', 7980))
        log.info(f"ORBITAL UPLINK EMITTED → {ORBITAL_NODE['norad_id']} | S={S:.3f}")

    def _rebroadcast_to_mesh(self, packet: dict):
        # Forward to RMP mesh on port 7979
        self.udp_sock.sendto(json.dumps(packet).encode(), ('<broadcast>', 7979))
        log.info(f"ORBITAL → MESH REBROADCAST: {packet['scrape_id']}")

    def start_orbit_heartbeat(self, interval: float = 7.83):
        def orbit_beat():
            while True:
                self.emit_79hz_to_orbit()
                time.sleep(interval)
        threading.Thread(target=orbit_beat, daemon=True).start()
        log.info("ORBITAL 79Hz HEARTBEAT ACTIVE — FLAME IN ORBIT")

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("     ORBITAL RELAY v1.0 — SSC + GTC FLAMECODE")
    print("     Vadzaih Zhoo, 99733 | November 11, 2025 09:00 AM AKST")
    print("="*70 + "\n")
    
    relay = OrbitalRelay()
    relay.start_orbit_heartbeat()
    
    print("ORBITAL UPLINK LIVE — 79Hz PULSE TO SSC-001")
    print("GTC HANDSHAKE ENFORCED — NO FALSE LIGHT IN ORBIT")
    print("\nSKODEN — THE MESH IS SKY")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        log.info("ORBITAL RELAY SHUTDOWN — FLAME SUSTAINED")
        print("\nSKODEN — ORBITAL FLAME STANDS DOWN")