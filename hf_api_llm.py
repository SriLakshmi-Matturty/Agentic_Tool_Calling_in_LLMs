import os
import requests

class HuggingFaceLLM:
    def __init__(self, model_name: str, token: str):
        self.model_name = model_name
        self.token = token
        self.base_url = "https://router.huggingface.co/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def generate(self, prompt: str, max_new_tokens: int = 256) -> str:
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_new_tokens
        }

        response = requests.post(self.base_url, headers=self.headers, json=payload)

        if response.status_code != 200:
            raise RuntimeError(f"Hugging Face API error {response.status_code}: {response.text}")

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
