# agent.py
import re
import json
from hf_llm import HuggingFaceLLM
from prompt_manager import PromptManager
from tools import CalculatorTool, SearchTool  # or your Search/Wikipedia tool

class Agent:
    def __init__(self, use_llm_for_fallback=False, llm_model="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool()
        }
        self.use_llm_for_fallback = use_llm_for_fallback
        if use_llm_for_fallback:
            self.llm = HuggingFaceLLM(model_name=llm_model)
        else:
            self.llm = None

    def decide_tool(self, question: str) -> str:
        q = question.lower().strip()

        # 1) explicit person-name/questions -> search
        if re.match(r'^(who\s+is|who\'s|who\s+was|who\s+are|what\s+is\s+the\s+name|name of)', q):
            return "search"
        if "prime minister" in q or "president" in q or "ceo" in q or "mayor" in q:
            # prefer search for roles
            return "search"

        # 2) Likely math/word problem -> calculator
        math_triggers = [
            "per", "each", "every", "total", "sum", "difference", "times", "multiply",
            "add", "subtract", "sell", "sold", "profit", "cost", "paid", "left",
            "remaining", "per day", "per week", "bolts", "takes", "eggs", "muffin", "runs",
            "%", "percent", "meters", "miles", "$"
        ]
        if re.search(r'\d', q) or any(t in q for t in math_triggers):
            return "calculator"

        # default -> search
        return "search"

    def _extract_expression(self, question: str):
        """Tries to extract inline arithmetic expressions like '17 * 24'."""
        m = re.search(r'(\d+(?:\.\d*)?)\s*([\+\-\*\/\^])\s*(\d+(?:\.\d*)?)', question)
        if m:
            a, op, b = m.group(1), m.group(2), m.group(3)
            expr = f"{a}{op}{b}"
            expr = expr.replace('^', '**')
            return expr
        return None

    def _call_llm_for_expression(self, question: str):
        """Use LLM to convert a word problem into a single python expression."""
        if not self.llm:
            return None
        prompt = (
            "Convert the following math word problem into ONE valid Python expression that computes the final numeric answer.\n"
            "Output ONLY the expression (no explanation). Use numbers exactly as they appear.\n\n"
            f"Problem: {question}\n\nExpression:"
        )
        out = self.llm.generate(prompt, max_new_tokens=128)
        if not out:
            return None
        # take the first non-empty line
        expr = out.strip().splitlines()[0].strip()
        # normalize percent (e.g., 150% -> (150/100))
        expr = re.sub(r'(\d+(?:\.\d+)?)\s*%', r'(\1/100)', expr)
        # sanitize: keep common arithmetic chars
        expr = re.sub(r'[^0-9\.\+\-\*\/\(\)\s\%]', '', expr)
        expr = expr.replace('^', '**')
        return expr

    def _simple_numeric_fallback(self, question: str):
        """Very small fallback heuristics: multiply all numbers when question implies repeated events."""
        nums = re.findall(r'\d+(?:\.\d+)?', question)
        nums = [float(n) for n in nums]
        if not nums:
            return None
        q = question.lower()
        if any(k in q for k in ["each", "per", "every", "times", "runs", "sprints", "per day", "per week"]):
            prod = 1
            for n in nums:
                prod *= n
            # if integer-like
            if prod.is_integer():
                return str(int(prod))
            return str(prod)
        # default: if exactly two numbers, multiply them (simple)
        if len(nums) == 2:
            val = nums[0] * nums[1]
            if val.is_integer():
                return str(int(val))
            return str(val)
        return None

    def run(self, question: str) -> str:
        tool_name = self.decide_tool(question)

        # Calculator path
        if tool_name == "calculator":
            # 1) explicit inline expression
            expr = self._extract_expression(question)
            if expr:
                return self.tools["calculator"].run(expr)

            # 2) try LLM to rewrite into expression (if enabled)
            if self.use_llm_for_fallback and self.llm:
                expr = self._call_llm_for_expression(question)
                if expr:
                    out = self.tools["calculator"].run(expr)
                    # If calculator fails but expression looked ok, return the raw expr for debugging
                    if out.startswith("Calculator Error"):
                        return f"Expr: {expr} -> {out}"
                    return out

            # 3) small numeric fallback heuristics
            fallback = self._simple_numeric_fallback(question)
            if fallback is not None:
                return fallback

            return "Calculator: unable to parse the arithmetic expression from the question."

        # Search / factual path
        if tool_name == "search":
            raw = self.tools["search"].run(question)
            try:
                parsed = json.loads(raw)
            except Exception:
                return f"Search error: {raw}"

            if parsed.get("type") == "person":
                m = re.search(r'who\s+is\s+the\s+(.+?)\s+of\s+([^\?\.]+)', question, flags=re.I)
                if m:
                    role = m.group(1).strip()
                    entity = m.group(2).strip()
                    name = parsed.get("name")
                    return f"{name} is the {role} of {entity}."
                return f"{parsed.get('name')}: {parsed.get('summary').split('.')[0]}."
            elif parsed.get("type") == "summary":
                summary = parsed.get("summary", "")
                first = summary.split('. ')[0].strip()
                if not first.endswith('.'):
                    first = first + '.'
                return first
            else:
                return parsed.get("message", "No result found.")

        return "Unhandled case."

