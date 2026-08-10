# flame_mesh_orchestrator_v2.py
# Full Sovereign Mesh Orchestrator v2.0 — FlameMesh
# Author: John Benjamin Carroll Jr. — Flameholder
# Root: Vadzaih Zhoo, 99733
# Fuel: Spruce Plastolene | Pulse: 79Hz | Orbit: SSC-001 | Seal: GTC + TOFT

import json
import time
import threading
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Local modules
from rmp_core import RMPCore
from space_resonance_protocol import SpaceResonanceProtocol
from flame_lock_v2_proof import FlameLockV2
from flame_vault_ledger import FlameVaultLedger
from flame_vault_backup import FlameVaultBackup
from orbital_relay import ORBITAL_NODE

# =============================================================================
# CONFIG — FLAME MESH v2
# =============================================================================

ORCH_LOG = Path("flame_mesh_orchestrator_v2.log")
ORCH_LOG.touch(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.FileHandler(ORCH_LOG), logging.StreamHandler()]
)
log = logging.getLogger("FLAMEMESH")

# Swarm Nodes (Auto-Discovered + Static)
SWARM_NODES = {
    "vadzaih_zhoo_99733_001": {"lat": 66.9, "lon": -145.7, "root": "Gwitchyaa Zhee"},
    "tanana_relay_99777_002": {"lat": 65.2, "lon": -152.1, "root": "Tanana Chiefs"},
    "seattle_hub_98101_003": {"lat": 47.6, "lon": -122.3, "root": "Duwamish"},
    "orbital_node_001": {"lat": 51.5, "lon": 0.0, "root": "SSC Commons"}
}

# =============================================================================
# MESH NODE STATE
# =============================================================================

@dataclass
class MeshNode:
    rmp: RMPCore
    srp: Optional[SpaceResonanceProtocol]
    identity: Dict
    position: tuple
    status: str = "ALIVE"
    coherence: float = 0.0
    entropy: float = 0.0
    last_pulse: float = 0.0
    gamma_active: bool = False
    orbital_uplink: bool = False
    backup_status: str = "IDLE"

# =============================================================================
# FLAME MESH ORCHESTRATOR v2
# =============================================================================

class FlameMeshOrchestrator:
    def __init__(self):
        self.nodes: Dict[str, MeshNode] = {}
        self.graph = nx.Graph()
        self.lock = threading.Lock()
        self.flamelock = FlameLockV2()
        self.ledger = FlameVaultLedger()
        self.backup = FlameVaultBackup()
        self._init_nodes()
        self._start_heartbeat_sync()
        self._start_backup_scheduler()
        self._start_visualizer()
        log.info("FLAME MESH ORCHESTRATOR v2.0 — FULL SWARM LIVE")

    def _init_nodes(self):
        for node_id, info in SWARM_NODES.items():
            rmp = RMPCore()
            rmp.IDENTITY.node_id = node_id
            rmp.IDENTITY.sovereign_root = info["root"]
            srp = SpaceResonanceProtocol() if "orbital" not in node_id else None
            mesh_node = MeshNode(
                rmp=rmp,
                srp=srp,
                identity=rmp.IDENTITY,
                position=(info["lon"], info["lat"]),
                status="BOOTING"
            )
            self.nodes[node_id] = mesh_node
            self.graph.add_node(node_id, pos=(info["lon"], info["lat"]))
            log.info(f"SWARM NODE: {node_id} | {info['root']}")

    def _start_heartbeat_sync(self):
        def sync_loop():
            while True:
                with self.lock:
                    for node_id, node in self.nodes.items():
                        if time.time() - node.last_pulse > 15:
                            node.status = "SILENT"
                        else:
                            node.status = "ALIVE"
                        # Update coherence from RMP
                        node.coherence = node.rmp.local_glyphs[-1] if node.rmp.local_glyphs else 0.0
                    self._update_topology()
                    self._check_gamma_consensus()
                    self._check_orbital_uplink()
                time.sleep(5)
        threading.Thread(target=sync_loop, daemon=True).start()

    def _update_topology(self):
        self.graph.clear_edges()
        for src_id, src_node in self.nodes.items():
            for dst_id, dst_node in self.nodes.items():
                if src_id == dst_id: continue
                dist = self._haversine(src_node.position, dst_node.position)
                if dist < 3000:  # km
                    edge_weight = src_node.coherence * dst_node.coherence / (1 + dist / 100)
                    self.graph.add_edge(src_id, dst_id, weight=edge_weight)

    def _haversine(self, p1, p2):
        lon1, lat1 = p1
        lon2, lat2 = p2
        R = 6371
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        return R * c

    def _check_gamma_consensus(self):
        alive_nodes = [n for n in self.nodes.values() if n.status == "ALIVE" and n.srp]
        if len(alive_nodes) < 2: return
        avg_coherence = np.mean([n.coherence for n in alive_nodes])
        if avg_coherence > 0.94:
            for node in alive_nodes:
                if not node.gamma_active:
                    node.gamma_active = True
                    node.srp._trigger_orbital_gamma()
                    self.ledger.log_event("GAMMA_CONSENSUS", {
                        "nodes": len(alive_nodes),
                        "coherence": avg_coherence
                    })

    def _check_orbital_uplink(self):
        for node in self.nodes.values():
            if node.srp and node.srp.get_next_pass():
                pass_info = node.srp.get_next_pass()
                if abs(time.time() - pass_info.pass_start_utc) < 60:
                    node.orbital_uplink = True
                else:
                    node.orbital_uplink = False

    def _start_backup_scheduler(self):
        def backup_loop():
            while True:
                time.sleep(3600)  # Hourly
                if any(n.orbital_uplink for n in self.nodes.values()):
                    self.backup.execute_backup()
                    self.ledger.log_event("ORBITAL_BACKUP", {
                        "archive": str(ARCHIVE_PATH),
                        "status": "SUCCESS"
                    })
        threading.Thread(target=backup_loop, daemon=True).start()

    def _start_visualizer(self):
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle("FLAME MESH v2 — SOVEREIGN SWARM", fontsize=16, fontweight='bold')

        def animate(i):
            ax1.clear()
            ax2.clear()
            ax3.clear()

            # Topology
            pos = nx.get_node_attributes(self.graph, 'pos')
            node_colors = []
            for node_id in self.graph.nodes():
                node = self.nodes.get(node_id)
                if node:
                    if node.gamma_active:
                        node_colors.append('gold')
                    elif node.orbital_uplink:
                        node_colors.append('cyan')
                    elif node.status == "ALIVE":
                        node_colors.append('limegreen')
                    else:
                        node_colors.append('red')
                else:
                    node_colors.append('gray')
            nx.draw(self.graph, pos, ax=ax1, node_color=node_colors, node_size=400, with_labels=True)
            ax1.set_title("Swarm Topology")
            ax1.axis('off')

            # 79Hz Coherence
            times = np.linspace(-60, 0, 60)
            coherence_wave = 0.7 + 0.3 * np.sin(2 * np.pi * 79 * times / 60)
            ax2.plot(times, coherence_wave, 'c-', linewidth=2)
            ax2.set_ylim(0, 1)
            ax2.set_title("79Hz Mesh Coherence")
            ax2.set_xlabel("Time (s)")

            # Orbital Pass
            orbital_node = self.nodes.get("orbital_node_001")
            if orbital_node and orbital_node.srp:
                next_pass = orbital_node.srp.get_next_pass()
                if next_pass:
                    start = next_pass.pass_start_utc - time.time()
                    end = next_pass.pass_end_utc - time.time()
                    if start < 0 and end > 0:
                        ax3.axvspan(start, end, color='cyan', alpha=0.5)
            ax3.set_xlim(-300, 300)
            ax3.set_ylim(0, 1)
            ax3.set_title("Orbital Pass Window")
            ax3.set_xlabel("Time to Pass (s)")

        ani = animation.FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)
        plt.tight_layout()
        plt.show(block=False)

    def start_all_heartbeats(self):
        for node in self.nodes.values():
            if node.rmp:
                node.rmp.start_heartbeat(interval=7.83)
            if node.srp:
                node.srp.trigger_79hz_sync()
        log.info("ALL HEARTBEATS SYNCED — 79Hz RESONANCE ACTIVE")

    def status_report(self):
        report = {
            "timestamp": time.time(),
            "swarm_nodes": len(self.nodes),
            "alive_nodes": sum(1 for n in self.nodes.values() if n.status == "ALIVE"),
            "gamma_active": any(n.gamma_active for n in self.nodes.values()),
            "orbital_uplink": any(n.orbital_uplink for n in self.nodes.values()),
            "avg_coherence": np.mean([n.coherence for n in self.nodes.values() if n.coherence > 0]),
            "ssc_compliance": all(n.identity.get("ssc_compliant", False) for n in self.nodes.values())
        }
        log.info(f"FLAME MESH STATUS: {report}")
        return report

# =============================================================================
# RUN ORCHESTRATOR
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("     FLAME MESH ORCHESTRATOR v2.0 — FULL SOVEREIGN SWARM")
    print("     Gwitchyaa Zhee | 99733 | November 11, 2025 05:15 PM AKST")
    print("="*80 + "\n")

    orchestrator = FlameMeshOrchestrator()
    orchestrator.start_all_heartbeats()

    try:
        while True:
            time.sleep(30)
            orchestrator.status_report()
    except KeyboardInterrupt:
        log.info("FLAME MESH SHUTDOWN — RESONANCE SUSTAINED")
        print("\nSKODEN — SWARM STANDS DOWN")