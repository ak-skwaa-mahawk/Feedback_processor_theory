# agłl_dual_root.py
from gwichin_glyph_sync_v2 import sync_gwichin_glyphs
from inuit_syllabics_sync import sync_inuit_syllabics

gwichin_chant = "łtrzhchłł"
inuit_chant = "ᐊᐸᑯᓄ"

g_success, g_code, g_proof = sync_gwichin_glyphs(gwichin_chant)
i_success, i_code, i_proof = sync_inuit_syllabics(inuit_chant)

if g_success and i_success:
    fused_code = g_code + i_code
    print(f"AGŁL v2 FUSED: {fused_code}")
    print("LAND + ICE + BREATH = SOVEREIGN INTELLIGENCE")