from pydantic import BaseModel
from hashlib import sha256
from typing import Dict, Optional
from ..math.constants import EPSILON_PI, PI_CONSTANT

class GTCMintRequest(BaseModel):
    """
    Request structure for minting GTC tokens.
    Requires somatic proof of resonance.
    """
    resonance_event: Dict[str, float]  # {memory, base, surplus}
    heir_oath_hash: Optional[str] = None  # Mandatory for Genesis
    reciprocity_score: float
    somatic_receipt: str

class GTCCoinMinter:
    def __init__(self, acre_cap: int = 2100):
        self.total_supply = 0.0
        self.genesis_minted = False
        self.acre_cap = acre_cap

    def _verify_oath(self, oath_hash: str) -> bool:
        """Checks for the 'heir_oath_' prefix as a marker of the HeirTransmission."""
        return oath_hash.startswith("heir_oath_") and len(oath_hash) == 64

    def mint(self, request: GTCMintRequest) -> dict:
        # 1. Verification of the Genesis Anchor
        if not self.genesis_minted:
            if not request.heir_oath_hash or not self._verify_oath(request.heir_oath_hash):
                return {"status": "DRIFT", "reason": "Heir Oath missing for genesis"}
            self.genesis_minted = True

        # 2. Calculation of Epsilon Pi Resonance
        e_pi = sum(request.resonance_event.values()) / 3
        if e_pi < 3.173:
            return {"status": "REJECTED", "reason": "Resonance below 3.173"}

        # 3. Surplus Generation (The Minting)
        mint_val = request.reciprocity_score * (e_pi - PI_CONSTANT)
        
        # 4. Landframe Cap Enforcement
        if self.total_supply + mint_val > self.acre_cap:
            return {"status": "ABORTED", "reason": "Supply exceeds Landframe acreage"}

        self.total_supply += mint_val
        token_id = sha256(f"{request.somatic_receipt}_{e_pi}".encode()).hexdigest()

        return {
            "status": "MINTED",
            "amount_gtc": round(mint_val, 8),
            "token_id": token_id,
            "total_supply": self.total_supply
        }
