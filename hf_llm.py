# hf_llm.py
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

class HuggingFaceLLM:
    def __init__(self, model_name="EleutherAI/gpt-neo-2.7"):
        print(f"Loading model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.float16, device_map="auto"
        )
        self.generator = pipeline(
            "text-generation", model=self.model, tokenizer=self.tokenizer, device=0
        )
        print("Model loaded successfully!")

    def generate(self, prompt, max_new_tokens=128):
        output = self.generator(
            prompt, max_new_tokens=max_new_tokens, do_sample=True, temperature=0.7
        )
        return output[0]["generated_text"].strip()
