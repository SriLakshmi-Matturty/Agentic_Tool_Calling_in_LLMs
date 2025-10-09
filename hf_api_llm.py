# hf_api_llm.py

class HuggingFaceAPI_LLM:
    def __init__(self, model_name, token=None):
        self.model_name = model_name
        self.token = token or os.getenv("HF_API_TOKEN")
        if not self.token:
            raise ValueError("Missing Hugging Face API token.")
        self.base_url = "https://router.huggingface.co/v1"

    def generate(self, prompt, max_new_tokens=256):
        """
        Each call is completely independent, no prior conversation.
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        # Ensure stateless generation
        payload = {
            "model": f"{self.model_name}:featherless-ai",
            "inputs": prompt,   # Use 'inputs' instead of chat messages
            "parameters": {
                "max_new_tokens": max_new_tokens,
                "return_full_text": False,
                "stop": ["####"]  # Stop at end of answer if needed
            }
        }

        response = requests.post(f"{self.base_url}/text-generation", headers=headers, json=payload)

        if response.status_code != 200:
            raise RuntimeError(f"Hugging Face API error {response.status_code}: {response.text}")

        return response.json()[0]["generated_text"]
