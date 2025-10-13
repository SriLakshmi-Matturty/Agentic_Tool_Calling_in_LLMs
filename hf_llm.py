from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

class LocalLLM:
    def __init__(self, model_name: str = "mistralai/Mistral-7B-Instruct-v0.2", device: str = None):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        print(f"Loading model {model_name} on {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )

        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device_map="auto"
        )

    def generate(self, prompt: str, max_new_tokens: int = 256) -> str:
        output = self.pipe(prompt, max_new_tokens=max_new_tokens, do_sample=True, temperature=0.3)
        return output[0]["generated_text"].replace(prompt, "").strip()
