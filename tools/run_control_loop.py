import sys
import os
import time
import socket
import struct

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.raft_governance import RaftEngine

def start_control_plane(engine: RaftEngine):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 9999))
    sock.settimeout(0.005)

    target_dt = 1.0 / 79.0
    print(f"[*] Control Loop locked at 79.0 Hz (Slice: {target_dt*1000:.3f} ms)")

    try:
        while True:
            t_start = time.perf_counter()
            state = engine.state_machine.get_runtime_snapshot()

            try:
                data, addr = sock.recvfrom(1024)
                if len(data) == 58:
                    u16 = struct.unpack('>29H', data)
                    live_phase = [round(x / 65535.0, 4) for x in u16[1:7]]
                else:
                    live_phase = state['phase_vector']
            except socket.timeout:
                live_phase = state['phase_vector']

            t_elapsed = time.perf_counter() - t_start
            t_sleep = target_dt - t_elapsed
            if t_sleep > 0:
                time.sleep(t_sleep)

    except KeyboardInterrupt:
        print("\n[*] Control Loop stopped cleanly.")
    finally:
        sock.close()

if __name__ == "__main__":
    node = RaftEngine(node_id="node-1", peers=["node-1", "node-2", "node-3"])
    start_control_plane(node)
