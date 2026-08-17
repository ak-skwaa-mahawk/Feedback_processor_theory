import os
import json
import time
import threading
from typing import List, Dict, Any, Optional, Tuple

class RaftLogEntry:
    def __init__(self, index: int, term: int, timestamp_ns: int, command_type: str, payload: Dict[str, Any], signature: str = ""):
        self.index = index
        self.term = term
        self.timestamp_ns = timestamp_ns
        self.command_type = command_type
        self.payload = payload
        self.signature = signature

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "term": self.term,
            "timestamp_ns": self.timestamp_ns,
            "command_type": self.command_type,
            "payload": self.payload,
            "signature": self.signature
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RaftLogEntry":
        return cls(
            index=data["index"],
            term=data["term"],
            timestamp_ns=data["timestamp_ns"],
            command_type=data["command_type"],
            payload=data["payload"],
            signature=data.get("signature", "")
        )

class DeterministicStateMachine:
    def __init__(self):
        self.cycle_id: int = 0
        self.frequency_hz: float = 79.0
        self.r_chase: float = 1.9427
        self.phase_vector: List[float] = [0.0] * 6
        self.damping_coefficients: Dict[str, float] = {"k_p": 0.042, "k_d": 0.018}
        self.signer_root: str = "99733-Q"
        self.last_applied_index: int = 0
        self.safety_tripped: bool = False

    def apply(self, entry: RaftLogEntry):
        payload = entry.payload
        if entry.command_type == "GOVERNANCE_STEP":
            self.cycle_id = payload.get("cycle_id", self.cycle_id)
            self.frequency_hz = payload.get("frequency_hz", self.frequency_hz)
            self.r_chase = payload.get("r_chase", self.r_chase)
            self.phase_vector = payload.get("phase_vector", self.phase_vector)
            self.damping_coefficients = payload.get("damping_coefficients", self.damping_coefficients)
            self.signer_root = payload.get("signer_root", self.signer_root)
        elif entry.command_type == "SAFETY_TRIP":
            self.safety_tripped = True
            self.damping_coefficients = {"k_p": 1.0, "k_d": 1.0}
        self.last_applied_index = entry.index

    def get_runtime_snapshot(self) -> Dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "frequency_hz": self.frequency_hz,
            "r_chase": self.r_chase,
            "phase_vector": list(self.phase_vector),
            "damping_coefficients": dict(self.damping_coefficients),
            "signer_root": self.signer_root,
            "safety_tripped": self.safety_tripped,
            "applied_index": self.last_applied_index
        }

class RaftEngine:
    def __init__(self, node_id: str, peers: List[str], storage_dir: str = "raft_storage", max_log_window: int = 1000):
        self.node_id = node_id
        self.peers = peers
        self.storage_dir = storage_dir
        self.max_log_window = max_log_window
        os.makedirs(storage_dir, exist_ok=True)

        self.current_term: int = 0
        self.voted_for: Optional[str] = None
        self.log: List[RaftLogEntry] = []
        
        self.commit_index: int = 0
        self.last_applied: int = 0

        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}

        self.state_machine = DeterministicStateMachine()
        self._lock = threading.RLock()
        
        self.log_file = os.path.join(self.storage_dir, "wal.jsonl")
        self.snapshot_file = os.path.join(self.storage_dir, "snapshot.json")
        self._recover_state()

    def _recover_state(self):
        with self._lock:
            if os.path.exists(self.snapshot_file):
                with open(self.snapshot_file, "r") as f:
                    snap = json.load(f)
                    self.current_term = snap.get("term", 0)
                    self.last_applied = snap.get("last_included_index", 0)
                    self.commit_index = self.last_applied
                    sm_data = snap.get("state_machine", {})
                    self.state_machine.cycle_id = sm_data.get("cycle_id", 0)
                    self.state_machine.frequency_hz = sm_data.get("frequency_hz", 79.0)
                    self.state_machine.r_chase = sm_data.get("r_chase", 1.9427)
                    self.state_machine.phase_vector = sm_data.get("phase_vector", [0.0] * 6)
                    self.state_machine.damping_coefficients = sm_data.get("damping_coefficients", {})
                    self.state_machine.signer_root = sm_data.get("signer_root", "99733-Q")
                    self.state_machine.last_applied_index = self.last_applied

            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    for line in f:
                        if line.strip():
                            entry = RaftLogEntry.from_dict(json.loads(line))
                            self.log.append(entry)
                            if entry.index > self.last_applied:
                                self.state_machine.apply(entry)
                                self.last_applied = entry.index
                                self.commit_index = entry.index
                                self.current_term = max(self.current_term, entry.term)

    def _persist_entry(self, entry: RaftLogEntry):
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def propose(self, command_type: str, payload: Dict[str, Any], signature: str = "") -> Optional[RaftLogEntry]:
        with self._lock:
            last_index = self.log[-1].index if self.log else self.last_applied
            new_entry = RaftLogEntry(
                index=last_index + 1,
                term=self.current_term,
                timestamp_ns=time.time_ns(),
                command_type=command_type,
                payload=payload,
                signature=signature
            )
            self.log.append(new_entry)
            self._persist_entry(new_entry)
            self.match_index[self.node_id] = new_entry.index
            self._try_advance_commit()
            return new_entry

    def handle_append_entries(
        self, term: int, leader_id: str, prev_log_index: int,
        prev_log_term: int, entries: List[Dict[str, Any]], leader_commit: int
    ) -> Tuple[bool, int]:
        with self._lock:
            if term < self.current_term:
                return False, self.current_term

            if term > self.current_term:
                self.current_term = term
                self.voted_for = None

            if prev_log_index > 0:
                matching_entry = None
                for e in self.log:
                    if e.index == prev_log_index:
                        matching_entry = e
                        break
                if prev_log_index > self.last_applied and (not matching_entry or matching_entry.term != prev_log_term):
                    return False, self.current_term

            for raw in entries:
                entry = RaftLogEntry.from_dict(raw)
                existing = [e for e in self.log if e.index == entry.index]
                if existing and existing[0].term != entry.term:
                    idx = self.log.index(existing[0])
                    self.log = self.log[:idx]
                if not any(e.index == entry.index for e in self.log):
                    self.log.append(entry)
                    self._persist_entry(entry)

            if leader_commit > self.commit_index:
                last_new_index = self.log[-1].index if self.log else self.last_applied
                self.commit_index = min(leader_commit, last_new_index)
                self._apply_to_state_machine()

            return True, self.current_term

    def _try_advance_commit(self):
        if not self.log:
            return
        match_values = list(self.match_index.values())
        match_values.sort()
        majority_idx = (len(self.peers) + 1) // 2
        median_match = match_values[-majority_idx] if match_values else self.commit_index

        if median_match > self.commit_index:
            for entry in reversed(self.log):
                if entry.index == median_match and entry.term == self.current_term:
                    self.commit_index = median_match
                    self._apply_to_state_machine()
                    break

    def _apply_to_state_machine(self):
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            for entry in self.log:
                if entry.index == self.last_applied:
                    self.state_machine.apply(entry)
                    break
        
        if len(self.log) > self.max_log_window:
            self.compact_log()

    def compact_log(self):
        with self._lock:
            if not self.log:
                return
            snapshot_data = {
                "last_included_index": self.last_applied,
                "term": self.current_term,
                "timestamp_ns": time.time_ns(),
                "state_machine": self.state_machine.get_runtime_snapshot()
            }
            with open(self.snapshot_file, "w") as f:
                json.dump(snapshot_data, f, indent=2)

            self.log = [e for e in self.log if e.index > self.last_applied]
            with open(self.log_file, "w") as f:
                for entry in self.log:
                    f.write(json.dumps(entry.to_dict()) + "\n")
