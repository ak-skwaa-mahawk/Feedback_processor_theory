#!/usr/bin/env python3
import socket
import struct
import time
import logging
from dataclasses import dataclass, field
from typing import Dict

ALLOWED_NODE        = "192.168.1.231"
LISTEN_IP           = "0.0.0.0"
LISTEN_PORT         = 9999
FRAME_SIZE          = 58
MIN_PACKET_INTERVAL = 0.005

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("tordial.telemetry")

@dataclass
class State:
    last_seq: int = -1
    last_packet_time: float = 0.0
    start_time: float = field(default_factory=time.time)

state = State()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((LISTEN_IP, LISTEN_PORT))
sock.settimeout(2.0)

log.info("Telemetry ingress active | listen=%s:%d | allow=%s", LISTEN_IP, LISTEN_PORT, ALLOWED_NODE)

try:
    while True:
        try:
            data, addr = sock.recvfrom(128)
            now = time.time()
            src_ip = addr[0]

            if src_ip != ALLOWED_NODE:
                log.warning("Rejected IP: %s", src_ip)
                continue

            if (now - state.last_packet_time) < MIN_PACKET_INTERVAL:
                continue
            state.last_packet_time = now

            if len(data) != FRAME_SIZE:
                log.warning("Rejected length: %d bytes from %s", len(data), src_ip)
                continue

            u16 = struct.unpack(">29H", data)
            seq = u16[0]

            if state.last_seq != -1 and (seq <= state.last_seq and (state.last_seq - seq) < 60000):
                log.warning("Rejected sequence: %d (last: %d)", seq, state.last_seq)
                continue
            state.last_seq = seq

            norm = [round(x / 65535.0, 4) for x in u16[1:7]]

            if not all(0.0 <= ch <= 1.0 for ch in norm):
                log.warning("Rejected range: %s", norm)
                continue

            log.info("Node %s (seq: %d) | Phase Vector: %s", src_ip, seq, norm)

        except socket.timeout:
            pass
except KeyboardInterrupt:
    log.info("Monitor terminated.")
finally:
    sock.close()
