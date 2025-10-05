# hf_llm.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class HuggingFaceLLM:
    def __init__(self, model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        print(f"Loading model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        self.device = self.model.device

    def generate(self, prompt: str, max_new_tokens=128):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # If model echoes prompt, drop the prompt prefix
        if text.startswith(prompt):
            text = text[len(prompt):].strip()
        return text.strip()
