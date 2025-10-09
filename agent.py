# agent.py
import re
import json
from hf_api_llm import HuggingFaceAPI_LLM
from prompt_manager import PromptManager
from tools import CalculatorTool, SearchTool

class Agent:
    def __init__(self, use_llm_for_fallback=False, llm_model="mistralai/Mistral-7B-Instruct-v0.2", token=None):
        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool()
        }
        self.use_llm_for_fallback = use_llm_for_fallback
        if use_llm_for_fallback:
            self.llm = HuggingFaceAPI_LLM(model_name=llm_model, token=token)
        else:
            self.llm = None

    def decide_tool(self, question: str) -> str:
        q = question.lower()
        if re.search(r'\d+\s*[\+\-\\/\^]\s\d+', q):
            return "calculator"
        if any(w in q for w in ["cost", "price", "paid", "how much", "how many", "total", "worth", "dollars", "$", "rupees"]):
            nums = re.findall(r'\d+\.?\d*', q)
            if len(nums) >= 2:
                return "calculator"
        return "search"

    def _extract_expression(self, question: str):
        """
        If question includes an inline arithmetic expression like '17 * 24' return it.
        """
        m = re.search(r'(\d+(?:\.\d*)?)\s*([\+\-\\/\^])\s(\d+(?:\.\d*)?)', question)
        if m:
            a, op, b = m.group(1), m.group(2), m.group(3)
            expr = f"{a}{op}{b}"
            expr = expr.replace('^', '**')  # for exponentiation
            return expr
        return None

    def run(self, question: str) -> str:
        tool_name = self.decide_tool(question)

        if tool_name == "calculator":
            # Use LLM few-shot prompt for multi-step problems
            if self.use_llm_for_fallback and self.llm:
                prompt = PromptManager.calculator_few_shot_prompt(question)
                reasoning = self.llm.generate(prompt, max_new_tokens=256)
                return reasoning.strip()

            # Fallback to simple inline expression
            expr = self._extract_expression(question)
            if expr:
                return self.tools["calculator"].run(expr)

            return "Calculator: unable to reason or parse expression."

        if tool_name == "search":
            # Use LLM few-shot prompt for search
            if self.use_llm_for_fallback and self.llm:
                prompt = PromptManager.search_few_shot_prompt(question)
                answer = self.llm.generate(prompt, max_new_tokens=128)
                return answer.strip()

            # Fallback to tools
            raw = self.tools["search"].run(question)
            try:
                parsed = json.loads(raw)
                return parsed.get("summary", "No result found.")
            except Exception:
                return f"Search error: {raw}"

        return "Unhandled case."
