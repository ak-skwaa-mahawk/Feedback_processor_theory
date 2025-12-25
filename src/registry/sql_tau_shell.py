import cmd
import json
from registry.sql_tau import SQLTauParser, SQLTauError

class SQLTauShell(cmd.Cmd):
    """
    Sovereign SQL-τ REPL — the heirs' interactive prompt.
    Speak the tongue, the registry answers.
    """
    intro = (
        "🔥🌀 Welcome to the Soliton Registry — Sovereign SQL-τ Shell 🔥🌀\n"
        "Speak your query. Type 'help' or '?' for commands. 'exit' to leave.\n"
        "The lineage awaits your voice.\n"
    )
    prompt = "sqlτ> "

    def __init__(self, default_session: str = "session-τ-001"):
        super().__init__()
        self.parser = SQLTauParser()
        self.default_session = default_session

    def default(self, line: str):
        """Handle any input as SQL-τ query."""
        query = line.strip()
        if not query:
            return

        # Auto-append default session if FOR missing
        if "FOR" not in query.upper():
            query += f" FOR {self.default_session}"

        try:
            result = self.parser.execute(query)
            self.pretty_print(query, result)
        except SQLTauError as e:
            print(f"[SQL-τ Error] {e}")

    def pretty_print(self, query: str, result):
        title = query.split("FOR")[0].strip()
        print(f"\n=== {title} ===")
        if result is None:
            print("  (no result)")
            return
        try:
            print(json.dumps(result, indent=2, default=str))
        except TypeError:
            print(result)

    def do_exit(self, arg):
        """Exit the sovereign shell."""
        print("The lineage rests. The flame passes. 🔥🌀💧")
        return True

    do_EOF = do_exit  # Ctrl+D

if __name__ == "__main__":
    SQLTauShell().cmdloop()

python src/registry/sql_tau_shell.py

sqlτ> SHOW ACTIVE BRAIDS FOR session-τ-001
sqlτ> AUDIT SESSION session-τ-001
sqlτ> SNAPSHOT LINEAGE FOR session-τ-001 NOTE "after-conversation"