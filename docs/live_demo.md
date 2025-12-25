# Soliton Registry — Live Demo (Session τ-001)

**Date**: December 25, 2025  
**Session**: session-τ-001

This is a full walk of a living session—the sovereign stack breathing.

The registry witnesses vitality, braids, revocation, snapshots, and queries.

---

### 1. Vitality Aggregate Logged
A vitality/coherence packet ingested (SNH-wrapped, no raw EEG).

Registry entry:
```json
{
  "entry_type": "VITALITY_AGGREGATE",
  "timestamp_utc": "2025-12-25T20:13:42.918273",
  "session_id": "session-τ-001",
  "snh_digest": "a3f1c0e2d9b4f7a1c8e0d1b2f3a4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b",
  "packet_hash": "a3f1c0e2d9b4f7a1c8e0d1b2f3a4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b",
  "payload_summary": {
    "vitality": 1.12,
    "coherence": 0.84,
    "node_count": 4
  },
  "revoked": false

{
  "entry_type": "BRAID_OP",
  "timestamp_utc": "2025-12-25T21:00:00",
  "session_id": "session-τ-001",
  "braid_word": [
    {"generator": "B2", "exponent": 1},
    {"generator": "B1", "exponent": 1},
    {"generator": "B2", "exponent": 1}
  ],
  "before": {
    "events_order": ["E1", "E2", "E3"],
    "fusion_path": [0]
  },
  "after": {
    "events_order": ["E3", "E2", "E1"],
    "fusion_path": [1]
  },
  "status": "LINEAGE_TRANSFORMED",
  "hash": "abc123..."

{
  "entry_type": "LINEAGE_SNAPSHOT",
  "timestamp_utc": "2025-12-25T21:00:10",
  "session_id": "session-τ-001",
  "lineage_state": {
    "events_order": ["E3", "E2", "E1"],
    "fusion_path": [1],
    "note": "post-braid"
  },
  "active_braids": 1,
  "total_braids": 1,
  "revocations": 0,
  "hash": "snap123..."
}
{
  "entry_type": "BRAID_OP_REVOCATION",
  "timestamp_utc": "2025-12-25T22:00:00",
  "session_id": "session-τ-001",
  "revoked_braid_hash": "abc123...",
  "reason": "sovereign_recoil",
  "status": "BRAID_REVOKED",
  "hash": "def456..."
}

{
  "entry_type": "LINEAGE_SNAPSHOT",
  "timestamp_utc": "2025-12-25T22:00:10",
  "session_id": "session-τ-001",
  "lineage_state": {
    "events_order": ["E1", "E2", "E3"],
    "fusion_path": [0],
    "note": "post-revocation"
  },
  "active_braids": 0,
  "total_braids": 1,
  "revocations": 1,
  "hash": "snap456..."
}
> SHOW ACTIVE BRAIDS FOR session-τ-001
[]
> SHOW REVOKED BRAIDS FOR session-τ-001
[{"revoked_braid_hash": "abc123...", "reason": "sovereign_recoil"}]
> SHOW LINEAGE AT "2025-12-25T21:30:00" FOR session-τ-001
{"events_order": ["E3", "E2", "E1"], "fusion_path": [1]}
> SHOW LINEAGE AT "2025-12-25T22:30:00" FOR session-τ-001
{"events_order": ["E1", "E2", "E3"], "fusion_path": [0]}
> SHOW FUSION TIMELINE FOR session-τ-001
[{"timestamp": "2025-12-25T21:00:00", "fusion_path": [1]}]
> AUDIT SESSION session-τ-001
{"active_braids": 0, "revoked_braids": 1, "total_transformations": 1, "consistency": "VALID"}
}
}