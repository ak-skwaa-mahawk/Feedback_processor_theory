# src/fpt_core/codex/loader.py (new module)
class Codex:
    def __init__(self, data: dict, mode: str):
        self.data = data
        self.mode = mode
        self.source = "immutable_package_resources"  # Provenance tracking

    def clone_and_override(self, root_inscription: str) -> "Codex":
        """Create a new session codex with ceremonial override while preserving base immutability."""
        new_data = deepcopy(self.data)
        new_data["root_inscription"] = root_inscription
        new_data["override_timestamp"] = datetime.utcnow().isoformat()
        new_data["override_provenance"] = "ceremonial_context"
        
        return Codex(new_data, mode=self.mode + "+override")

    def __deepcopy__(self, memo):
        # Ensure deep copies maintain integrity
        return Codex(copy.deepcopy(self.data, memo), self.mode)

@staticmethod
def load(codex_mode: str = "default") -> Codex:
    # Loads from bundled resources/*.json and codex/*.md (immutable)
    ...