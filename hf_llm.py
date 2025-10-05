# hf_llm.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class HFLLM:
    def __init__(self, model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0", device=None):
        print(f"Loading model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def generate(self, prompt: str, max_new_tokens=80):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove prompt prefix if model echoes prompt back
        if text.startswith(prompt):
            text = text[len(prompt):].strip()
        return text.strip()
