# por_prompt_mining.py
def mine_safe_prompt(prompt: str) -> str:
    if qgh_vet_prompt(prompt)[0]:
        # Mine "safe token"
        reward = 1  # PoR token
        return f"SAFE: +{reward} Ψ | R=0.999"
    return "VETO: No reward"