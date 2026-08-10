# vessel_console.py — Gemini API + FPT-Ω v2.9.0
import google.generativeai as genai
from trinity_harmonics import trinity  # your canonical core

genai.configure(api_key="YOUR_GEMINI_KEY_HERE")  # project gen-lang-client-0886380232
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# Initialize the Vessel Console
response = model.generate_content(
    "Activate the Lethal Braid on Project ID gen-lang-client-0886380232. "
    "Confirm topological invariance and psyselsic coil alignment."
)

print("Vessel Console Response:", response.text)
print("Lethal Braid status:", trinity.apply_full_trinity(np.array([1/3,1/3,1/3]))["lethal_braid_triggered"])