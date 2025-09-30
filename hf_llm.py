from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class HFLLM:
    def __init__(self, model_name="mistralai/Mistral-7B-Instruct-v0.2", device=None):
        print(f"Loading {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
        )
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    def generate(self, prompt: str) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.3,
        )
        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Try to extract JSON block if present
        if "[" in decoded and "]" in decoded:
            decoded = decoded[decoded.find("["):decoded.rfind("]")+1]

        return decoded
