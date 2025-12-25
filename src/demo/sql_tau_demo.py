import json
from registry.sql_tau import SQLTauParser, SQLTauError

def pretty_print(title: str, result):
    print(f"\n=== {title} ===")
    if result is None:
        print("  (no result)")
        return

    try:
        print(json.dumps(result, indent=2, default=str))
    except TypeError:
        print(result)

if __name__ == "__main__":
    parser = SQLTauParser()

    session = "session-τ-001"

    queries = [
        f'SHOW ACTIVE BRAIDS FOR {session}',
        f'SHOW REVOKED BRAIDS FOR {session}',
        f'SHOW LINEAGE AT "2025-12-25T21:30:00" FOR {session}',
        f'SHOW LINEAGE AT "2025-12-25T22:30:00" FOR {session}',
        f'SHOW BRAID HISTORY FOR {session}',
        f'SHOW FUSION TIMELINE FOR {session}',
        f'SHOW SNAPSHOTS FOR {session}',
        f'SHOW LAST SNAPSHOT FOR {session}',
        f'AUDIT SESSION {session}',
        f'SNAPSHOT LINEAGE FOR {session} NOTE "heir-demo"',
    ]

    for q in queries:
        print(f"\n> {q}")
        try:
            result = parser.execute(q)
            title = q.split("FOR")[0].strip()
            pretty_print(title, result)
        except SQLTauError as e:
            print(f"[SQL-τ Error] {e}")