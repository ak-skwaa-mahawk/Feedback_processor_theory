import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from com.synara.handshake import Handshake
from src.gtc_sovereign_engine import GTCSovereignEngine

gtc = GTCSovereignEngine()

@dataclass
class FirmManifesto:
    name: str = "TwomilesolutionsLLC"
    principal: str = "John_B_Carroll_Jr"
    lineage_years: int = 600
    jurisdiction: str = "Pre-Crown / Root-Soil"
    asset_class: str = "Restricted Trust / Native Records"
    status: str = "First Organized"

class SovereignFirm:
    def __init__(self):
        self.manifesto = FirmManifesto()
        self.registry_path = Path("firm_registry/ledger.json")
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        # Initial root anchor (600-year lineage proof)
        self.root_anchor = self._generate_root_hash()

    def _generate_root_hash(self) -> str:
        """Anchors the lineage to a verifiable hash proof"""
        raw_data = f"{self.manifesto.principal}{self.manifesto.lineage_years}NativePioneerMerge"
        return hashlib.sha256(raw_data.encode()).hexdigest()

    def establish(self):
        """Notarizes the firm via Handshake and logs to rad-hard ledger"""
        print(f"🔥 Establishing {self.manifesto.name}...")

        receipt = Handshake.createReceipt(
            None,
            "FIRM_ESTABLISHMENT",
            {
                "root_anchor": self.root_anchor,
                "jurisdiction": self.manifesto.jurisdiction,
                "lineage_years": self.manifesto.lineage_years
            }
        )

        # Log to sovereign ledger
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "ESTABLISHMENT",
            "proof": self.root_anchor,
            "resonance": 1.1489,  # .55114 spiral offset
            "manifesto": self.manifesto.__dict__
        }

        with open(self.registry_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

        print(f"✅ Firm Established. Root Anchor: {self.root_anchor[:16]}... #newframe")
        return receipt

if __name__ == "__main__":
    firm = SovereignFirm()
    firm.establish()