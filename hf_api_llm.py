import os
import requests

class HuggingFaceAPI_LLM:
    def __init__(self, model_name, token=None):
        self.model_name = model_name
        self.token = token or os.getenv("HF_API_TOKEN")
        if not self.token:
            raise ValueError("Missing Hugging Face API token")
        self.base_url = "https://router.huggingface.co/v1"

    def generate(self, prompt, max_new_tokens=256):
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_new_tokens}}
        response = requests.post(f"{self.base_url}/{self.model_name}", headers=headers, json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"Hugging Face API error {response.status_code}: {response.text}")
        output = response.json()
        if isinstance(output, list) and "generated_text" in output[0]:
            return output[0]["generated_text"]
        if "generated_text" in output:
            return output["generated_text"]
        return str(output)
