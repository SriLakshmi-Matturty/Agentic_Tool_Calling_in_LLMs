# agent.py
import re
import json
from hf_api_llm import HuggingFaceAPI_LLM
from prompt_manager import PromptManager
from tools import CalculatorTool, SearchTool

class Agent:
    def __init__(self, use_llm_for_fallback=False, llm_model="mistralai/Mistral-7B-Instruct-v0.2", token=None):
        self.tools = {"calculator": CalculatorTool(), "search": SearchTool()}
        self.use_llm_for_fallback = use_llm_for_fallback
        self.llm = HuggingFaceAPI_LLM(model_name=llm_model, token=token) if use_llm_for_fallback else None

    def decide_tool(self, question: str) -> str:
        q = question.lower()
        if re.search(r'\d+\s*[\+\-\\/\^]\s*\d+', q):
            return "calculator"
        if any(w in q for w in ["cost", "price", "paid", "how much", "how many", "total", "worth", "dollars", "$", "rupees"]):
            nums = re.findall(r'\d+\.?\d*', q)
            if len(nums) >= 2:
                return "calculator"
        return "search"

    def _extract_expression(self, question: str):
        m = re.search(r'(\d+(?:\.\d*)?)\s*([\+\-\\/\^])\s*(\d+(?:\.\d*)?)', question)
        if m:
            a, op, b = m.group(1), m.group(2), m.group(3)
            expr = f"{a}{op}{b}".replace("^", "**")
            return expr
        return None

    def run(self, question: str) -> str:
        tool_name = self.decide_tool(question)

        if tool_name == "calculator":
            expr = self._extract_expression(question)
            if expr:
                return self.tools["calculator"].run(expr)

            if self.use_llm_for_fallback and self.llm:
                prompt = PromptManager.calculator_few_shot_prompt(question)
                reasoning = self.llm.generate(prompt, max_new_tokens=512)
                m = re.search(r'####\s*([0-9\.]+)', reasoning)
                return m.group(1) if m else reasoning.strip()

            return "Calculator: unable to parse expression."

        if tool_name == "search":
            if self.use_llm_for_fallback and self.llm:
                prompt = PromptManager.search_few_shot_prompt(question)
                return self.llm.generate(prompt, max_new_tokens=256).strip()

            raw = self.tools["search"].run(question)
            try:
                parsed = json.loads(raw)
                return parsed.get("summary", "No result found.")
            except Exception:
                return f"Search error: {raw}"

