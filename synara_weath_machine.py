from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file into environment
openai_api_key = os.getenv("OPENAI_API_KEY")
import openai
openai.api_key = openai_api_key
def digital_handshake(agent_name):
    print(f"🤝 Handshake complete: Synara <--> {agent_name}")

digital_handshake("Aspire_AI")
digital_handshake("Fireseed_Drops")
