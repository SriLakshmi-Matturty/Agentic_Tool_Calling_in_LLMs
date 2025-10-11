import re
from tools import CalculatorTool, SearchTool
from prompt_manager import PromptManager
from hf_llm import LocalLLM
import json

class Agent:
    def __init__(self, llm_model=None, serpapi_key=None):
        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool(serpapi_key)
        }
        self.llm = LocalLLM(model_name=llm_model)

    def decide_tool_and_expr(self, question: str):
        """
        Decide which tool to call based on question.
        Returns: (tool_name, expression/None)
        """

        # Quick numeric check
        simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
        if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
            print(f"[DEBUG] Detected simple numeric expression: {question}")
            return "calculator", question

        # Prompt LLM with JSON output requirement
        prompt = f"""
Classify the question as 'math' or 'factual'.
Respond ONLY in JSON format like:

{{"type": "math", "expression": "2+3"}}
or
{{"type": "factual", "expression": null}}

Q: {question}
A:
"""
        response = self.llm.generate(prompt, max_new_tokens=64).strip()
        print(f"[DEBUG] LLM response: {response}")

        # Parse JSON output safely
        try:
            parsed = json.loads(response)
            if parsed["type"] == "math" and parsed["expression"]:
                expr = parsed["expression"]
                if re.fullmatch(r"[\d\s\.\+\-\*/\(\)]+", expr):
                    print(f"[DEBUG] Using CalculatorTool for expression: {expr}")
                    return "calculator", expr
            return "search", None
        except json.JSONDecodeError:
            print("[DEBUG] Invalid JSON from LLM, defaulting to SearchTool")
            return "search", None

    def run(self, question: str):
        tool_name, expr = self.decide_tool_and_expr(question)
        tool = self.tools[tool_name]
        result = tool.execute(expr)
        return result
