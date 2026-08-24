import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"

class LocalAIResponse:
    def __init__(self, text):
        self.text = text

def generate_content(prompt):
    """
    Sends a prompt to the local Ollama instance running Llama 3 (or 3.1)
    and returns a mock object similar to Gemini's response object.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return LocalAIResponse(data.get("response", ""))
        else:
            print(f"Error from Local AI: {response.status_code} - {response.text}")
            return LocalAIResponse("")
    except Exception as e:
        print(f"Failed to connect to Local AI at {OLLAMA_API_URL}: {e}")
        return LocalAIResponse("")

# Create a mock 'gemini_model' object that exposes generate_content
class MockGeminiModel:
    def generate_content(self, prompt):
        return generate_content(prompt)

gemini_model = MockGeminiModel()
