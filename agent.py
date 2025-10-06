# agent.py
import re
import json
from hf_llm import HuggingFaceLLM
from prompt_manager import PromptManager
from tools import CalculatorTool, SearchTool

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
        q = question.lower()
        # If explicit arithmetic or expression present
        if re.search(r'\d+\s*[\+\-\\/\^]\s\d+', q):
            return "calculator"
        # Proportion/price style word problems -> calculator
        if any(w in q for w in ["cost", "price", "paid", "how much", "how many", "total", "worth", "dollars", "$", "rupees"]):
            # if question contains at least 2 numbers it's likely arithmetic/proportion
            nums = re.findall(r'\d+\.?\d*', q)
            if len(nums) >= 2:
                return "calculator"
        # otherwise treat as factual -> wikipedia
        return "search"

    def _solve_proportion(self, question: str):
        """
        Basic heuristic: if question contains exactly 3 numbers like [a, b, c],
        and form matches "a items for b$, ... for c items", compute c*(b/a).
        """
        nums = re.findall(r'\d+\.?\d*', question)
        if len(nums) >= 3:
            a = float(nums[0])
            b = float(nums[1])
            c = float(nums[2])
            # compute c * (b / a)
            try:
                val = c * (b / a)
                if val.is_integer():
                    val = int(val)
                return str(val)
            except Exception:
                return None
        return None

    def _extract_expression(self, question: str):
        """
        If question includes an inline arithmetic expression like '17 * 24' return it.
        """
        m = re.search(r'(\d+(?:\.\d*)?)\s*([\+\-\\/\^])\s(\d+(?:\.\d*)?)', question)
        if m:
            a, op, b = m.group(1), m.group(2), m.group(3)
            expr = f"{a}{op}{b}"
            expr = expr.replace('^', '')
            return expr
        return None

    def run(self, question: str) -> str:
        tool_name = self.decide_tool(question)
        # Calculator path
        if tool_name == "calculator":
            # 1) Try to extract explicit expression
            expr = self._extract_expression(question)
            if expr:
                out = self.tools["calculator"].run(expr)
                return out
            # 2) Proportion heuristic (common in GSM8K)
            prop = self._solve_proportion(question)
            if prop is not None:
                return prop
            # 3) Fall back: attempt to extract numbers and do simple operations: if 2 numbers -> maybe division or multiplication?
            nums = re.findall(r'\d+\.?\d*', question)
            if len(nums) == 2:
                # guess: maybe a per-unit price: "Weng earns $12 an hour ... 50 minutes" -> convert minutes to hours
                # handle special case: minutes/hours
                if "minute" in question or "minutes" in question:
                    try:
                        pay_per_hour = float(nums[0])
                        minutes = float(nums[1])
                        val = pay_per_hour * (minutes / 60.0)
                        if val.is_integer():
                            val = int(val)
                        return str(val)
                    except Exception:
                        pass
                # default: multiply?
                try:
                    val = float(nums[0]) * float(nums[1])
                    if val.is_integer():
                        val = int(val)
                    return str(val)
                except Exception:
                    pass
            # If still not resolved, optionally use LLM to produce expression (if enabled)
            if self.use_llm_for_fallback and self.llm:
                prompt = f"Rewrite this question as a single Python arithmetic expression only (no text):\nQuestion: {question}\nExpression:"
                expr_text = self.llm.generate(prompt, max_new_tokens=64)
                expr_text = expr_text.strip().splitlines()[0]
                # try to sanitize and evaluate
                expr_text = expr_text.replace('^', '')
                out = self.tools["calculator"].run(expr_text)
                return out
            return "Calculator: unable to parse the arithmetic expression from the question."

        # Wikipedia / factual path
        if tool_name == "search":
            raw = self.tools["search"].run(question)
            # raw is JSON-string according to our tool
            try:
                parsed = json.loads(raw)
            except Exception:
                return f"Search error: {raw}"

            if parsed.get("type") == "person":
                # If question is a 'Who is the <role> of <entity>' we try to craft a natural short answer
                m = re.search(r'who\s+is\s+the\s+(.+?)\s+of\s+([^\?\.]+)', question, flags=re.I)
                if m:
                    role = m.group(1).strip()
                    entity = m.group(2).strip()
                    name = parsed.get("name")
                    # e.g., "Droupadi Murmu is the president of India."
                    return f"{name} is the {role} of {entity}."
                # otherwise return name + short summary
                return f"{parsed.get('name')}: {parsed.get('summary').split('.')[0]}."
            elif parsed.get("type") == "summary":
                # return the first sentence of the summary as a concise answer
                summary = parsed.get("summary", "")
                first = summary.split('. ')[0].strip()
                if not first.endswith('.'):
                    first = first + '.'
                return first
            else:
                return parsed.get("message", "No result found.")
        return "Unhandled case."
