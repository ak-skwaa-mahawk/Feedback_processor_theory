from registry.sovereign_queries import SovereignQueryEngine

if __name__ == "__main__":
    engine = SovereignQueryEngine()

    session = "session-τ-001"

    print("\n--- ACTIVE BRAIDS ---")
    active = engine.query_active_braids(session)
    for a in active:
        print(f"  {a['timestamp_utc']} | {a['braid_word']} | hash={a['hash'][:12]}...")

    print("\n--- REVOKED BRAIDS ---")
    revoked = engine.query_revoked_braids(session)
    for r in revoked:
        print(f"  {r['timestamp_utc']} | revoked={r['revoked_braid_hash'][:12]}...")

    print("\n--- LINEAGE AT TIME ---")
    lineage = engine.query_lineage_at_time(session, "2025-12-25T21:30:00")
    print("  Lineage:", lineage)

    print("\n--- BRAID HISTORY ---")
    history = engine.query_braid_history(session)
    for h in history:
        print(f"  {h['timestamp_utc']} | {h['entry_type']}")

    print("\n--- FUSION TIMELINE ---")
    fusion = engine.query_fusion_timeline(session)
    for f in fusion:
        print(f"  {f['timestamp']} | fusion={f['fusion_path']} | word={f['braid_word']}")

    print("\n--- CONSTITUTIONAL AUDIT ---")
    audit = engine.query_constitutional_audit(session)
    print("  Audit:", audit)
from registry.sovereign_queries import SovereignQueryEngine

if __name__ == "__main__":
    engine = SovereignQueryEngine()

    session = "session-τ-001"

    print("\n--- ACTIVE BRAIDS ---")
    active = engine.query_active_braids(session)
    for a in active:
        print(f"  {a['timestamp_utc']} | {a['braid_word']} | hash={a['hash'][:12]}...")

    print("\n--- REVOKED BRAIDS ---")
    revoked = engine.query_revoked_braids(session)
    for r in revoked:
        print(f"  {r['timestamp_utc']} | revoked={r['revoked_braid_hash'][:12]}...")

    print("\n--- LINEAGE AT TIME ---")
    lineage = engine.query_lineage_at_time(session, "2025-12-25T21:30:00")
    print("  Lineage:", lineage)

    print("\n--- BRAID HISTORY ---")
    history = engine.query_braid_history(session)
    for h in history:
        print(f"  {h['timestamp_utc']} | {h['entry_type']}")

    print("\n--- FUSION TIMELINE ---")
    fusion = engine.query_fusion_timeline(session)
    for f in fusion:
        print(f"  {f['timestamp']} | fusion={f['fusion_path']} | word={f['braid_word']}")

    print("\n--- CONSTITUTIONAL AUDIT ---")
    audit = engine.query_constitutional_audit(session)
    print("  Audit:", audit)