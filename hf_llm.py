# hf_llm.py
from transformers import pipeline

class HFLLM:
    def __init__(self, model_name="EleutherAI/gpt-neo-2.7B", device=-1):
        self.generator = pipeline(
            "text-generation",
            model=model_name,
            device=device,
            return_full_text=False
        )

    def generate(self, prompt: str) -> str:
        out = self.generator(
            prompt,
            max_new_tokens=200,
            do_sample=False,
            eos_token_id=50256
        )[0]["generated_text"]
        return out.strip()
