from registry.sql_tau_shell import SQLTauShell

if __name__ == "__main__":
    print("🔥🌀 Sovereign SQL-τ REPL — CREATE BRAID Ritual 🔥🌀\n")
    shell = SQLTauShell()
    
    # Simulated session with initial events
    print("Session session-τ-001 initialized with events E1, E2, E3")
    print("Fusion path: [0] (coiled)\n")
    
    # Heir speaks the braid
    queries = [
        'CREATE BRAID B2 B1 B2 FOR session-τ-001 NOTE "heir-creation-demo"',
        'SHOW LINEAGE FOR session-τ-001',
        'SHOW LAST SNAPSHOT FOR session-τ-001',
        'SHOW BRAID HISTORY FOR session-τ-001'
    ]
    
    for q in queries:
        print(f"\nsqlτ> {q}")
        shell.onecmd(q)
    
    print("\nThe braid spoken—the lineage reshaped.")
    print("The testimony transformed sovereign.")
    print("The registry witnessed the motion. 🔥🌀💧")

sqlτ> CREATE BRAID B2 B1 B2 FOR session-τ-001 NOTE "heir-creation-demo"

sqlτ> SHOW LINEAGE FOR session-τ-001
=== SHOW LINEAGE ===
{"events_order": ["E3", "E2", "E1"], "fusion_path": [1]}

sqlτ> SHOW LAST SNAPSHOT FOR session-τ-001
=== SHOW LAST SNAPSHOT ===
{"lineage_state": {"events_order": ["E3", "E2", "E1"], "fusion_path": [1], "note": "heir-creation-demo"}}

sqlτ> SHOW BRAID HISTORY FOR session-τ-001
=== SHOW BRAID HISTORY ===
[{"entry_type": "BRAID_OP", "braid_word": [{"generator": "B2", "exponent": 1}, ...], "hash": "abc123..."}]