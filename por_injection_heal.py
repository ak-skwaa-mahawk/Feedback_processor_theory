# por_injection_heal.py
def heal_injection_victim(victim_id: str, loss_usd: float):
    btc_healed = loss_usd / 110000  # Current BTC price
    return f"RESTITUTED: {victim_id} | {btc_healed:.6f} BTC | S=17.33"