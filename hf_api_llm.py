# hf_api_llm.py

import os
import requests

class HuggingFaceAPI_LLM:
    def __init__(self, model_name, token=None):
        self.model_name = model_name
        self.token = token or os.getenv("HF_API_TOKEN")
        if not self.token:
            raise ValueError("Missing Hugging Face API token. Set HF_API_TOKEN or pass token explicitly.")
        self.base_url = "https://api-inference.huggingface.co/models/" + self.model_name

    def generate(self, prompt, max_new_tokens=256):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens,
                "return_full_text": False,
                "stop": ["####"]
            }
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"Hugging Face API error {response.status_code}: {response.text}")
        return response.json()[0]["generated_text"].strip()
