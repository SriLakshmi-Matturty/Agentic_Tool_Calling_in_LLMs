# hf_api_llm.py
import requests
import json
import os

class HuggingFaceAPI_LLM:
    def __init__(self, model_name="mistralai/Mistral-7B-Instruct-v0.2", token=None):
        self.model_name = model_name
        self.token = token or os.getenv("HF_API_TOKEN")
        if not self.token:
            raise ValueError("Missing Hugging Face API token. Set HF_API_TOKEN env variable or pass explicitly.")

    def generate(self, prompt: str, max_new_tokens=256):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens,
                "temperature": 0.3,
                "return_full_text": False
            }
        }

        url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise RuntimeError(f"Hugging Face API error {response.status_code}: {response.text}")

        try:
            data = response.json()
            return data[0]["generated_text"].strip()
        except Exception:
            return json.dumps(data, indent=2)
