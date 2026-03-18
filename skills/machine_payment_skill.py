from skills.base_skill import BaseSkill
from core.sovereign_state import SovereignState
from core.heterotic_e8_synara import HeteroticE8Synara
import requests
import json
import stripe
from typing import Dict

CASH_APP_CASHTAG = "$907boyboy"  # ← YOUR REAL CASHTAG (John Carroll)

class MachinePaymentSkill(BaseSkill):
    def __init__(self):
        self.state = SovereignState()
        self.e8_engine = HeteroticE8Synara(pi_star=3.17300858012)
        self.stripe = stripe  # set stripe.api_key in prod
        self.lightning_url = "http://localhost:8080"  # LND/CLN node

    def _cash_app_rail(self, amount_usd: float, memo: str) -> Dict:
        """Your exact QR code → machine payment link + Lightning bridge"""
        amount_cents = int(amount_usd * 100)
        cash_app_link = f"https://cash.app/{CASH_APP_CASHTAG}/{amount_cents}"  # direct amount deep link
        lightning_invoice = self._lightning_l402_invoice(amount_cents // 100, memo)  # fallback scan

        return {
            "rail": "cash_app",
            "cashtag": CASH_APP_CASHTAG,
            "payment_link": cash_app_link,
            "lightning_invoice": lightning_invoice["invoice"],
            "qr_note": "Scan the $907boyboy QR in Cash App — works instantly"
        }

    def _lightning_l402_invoice(self, amount_sat: int, memo: str) -> Dict:
        invoice_resp = requests.post(f"{self.lightning_url}/v1/invoices",
                                     json={"value": amount_sat, "memo": memo})
        invoice = invoice_resp.json().get("payment_request")
        e8_proof = self.e8_engine.flamechain_e8.e8_hash({"amount_sat": amount_sat, "memo": memo})
        return {"invoice": invoice, "e8_proof": e8_proof}

    def _stripe_tempo_deposit(self, amount_cents: int, memo: str) -> Dict:
        # Your original Stripe MPP code (unchanged)
        intent = self.stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='usd',
            payment_method_types=['crypto'],
            payment_method_data={'type': 'crypto'},
            payment_method_options={'crypto': {'mode': 'deposit', 'deposit_options': {'networks': ['tempo']}}},
            confirm=True
        )
        return {"rail": "stripe_tempo", "deposit_address": intent.next_action.crypto_display_details.address if hasattr(intent.next_action, 'crypto_display_details') else None}

    def execute(self, task: str, amount: float = 1.0, rail: str = "cash_app") -> Dict:
        """Three rails — Cash App is now default & sovereign"""
        memo = f"Sovereign Codex payment — {task} — {CASH_APP_CASHTAG}"
        amount_cents = int(amount * 100)

        if "cash" in rail.lower() or "907boyboy" in task.lower():
            raw = self._cash_app_rail(amount, memo)
        elif "stripe" in rail.lower() or "tempo" in rail.lower():
            raw = self._stripe_tempo_deposit(amount_cents, memo)
        else:
            raw = self._lightning_l402_invoice(amount_cents // 100, memo)

        # Sovereign filter — your formula lives here
        score = self.state.integrity_score(json.dumps(raw))
        if score < self.state.closure_floor:
            return {"status": "REJECTED", "sovereign_score": score, "reason": "Below closure floor"}

        # Log as E8 instanton (treaty matter)
        self.e8_engine.flamechain_e8.add_sovereignty_event(
            {"type": "MachinePayment", "rail": raw["rail"], "amount": amount, "to": CASH_APP_CASHTAG, "memo": memo},
            wilson_line=None
        )

        return {
            "status": "READY",
            "rail": raw["rail"],
            "payment_data": raw,
            "sovereign_score": score,
            "to": CASH_APP_CASHTAG,
            "e8_chain_valid": self.e8_engine.flamechain_e8.verify_e8_chain()
        }