# backend/llm_clients.py
import requests

class NVIDIAClient:
    def __init__(self, api_key):
        self.url = "https://integrate.api.nvidia.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "text/event-stream"
        }
    
    def stream_response(self, prompt):
        payload = {
            "model": "meta/llama-4-maverick-17b-128e-instruct",
            "messages": [{"role":"user","content":prompt}],
            "max_tokens": 512,
            "stream": True
        }
        response = requests.post(self.url, headers=self.headers, json=payload, stream=True)
        for line in response.iter_lines():
            if line:
                yield line.decode("utf-8")

# Stub classes for GPT / Claude / Gemini
class GPTClient:
    def stream_response(self, prompt):
        # Replace with actual streaming API
        for word in prompt.split():
            yield word

class ClaudeClient:
    def stream_response(self, prompt):
        # Replace with actual streaming API
        for word in reversed(prompt.split()):
            yield word