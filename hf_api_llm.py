# hf_api_llm.py
import os
import requests

class HuggingFaceAPI_LLM:
    def __init__(self, model_name, token=None):
        self.model_name = model_name
        self.token = token or os.getenv("HF_API_TOKEN")
        if not self.token:
            raise ValueError("Missing Hugging Face API token. Set HF_API_TOKEN env variable or pass explicitly.")
        self.base_url = "https://router.huggingface.co/v1"

    def generate(self, prompt, max_new_tokens=256):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": f"{self.model_name}:featherless-ai",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_new_tokens,
        }

        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)

        if response.status_code != 200:
            raise RuntimeError(f"Hugging Face API error {response.status_code}: {response.text}")

        return response.json()["choices"][0]["message"]["content"]
