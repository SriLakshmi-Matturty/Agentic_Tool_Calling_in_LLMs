import re
from tools import CalculatorTool, SearchTool
from hf_llm import LocalLLM
import json
import math

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
        Returns: (tool_name, expression/query)
        """
    
        simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
        if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
            print(f"[DEBUG] Detected simple numeric expression: {question}")
            return "calculator", question
    
        prompt = f"""
    Classify the question as 'math' or 'factual'. Do not add extra questions just return json format only.
    Respond ONLY in JSON format like:
    
    {{"type": "math", "expression": "2+3"}}
    or
    {{"type": "factual", "expression": null}}
    
    Q: {question}
    A:
    """
        response = self.llm.generate(prompt, max_new_tokens=64).strip()
        print(f"[DEBUG] LLM response: {response}")
    
        try:
            parsed = json.loads(response)
    
            # Case 1: Math
            if parsed["type"] == "math" and parsed["expression"]:
                expr = parsed["expression"]
                if re.fullmatch(r"[\d\s\.\+\-\*/\(\)a-zA-Z]+", expr):
                    print(f"[DEBUG] Using CalculatorTool for expression: {expr}")
                    return "calculator", expr
    
            # Case 2: Factual (expression is null)
            elif parsed["type"] == "factual":
                print("[DEBUG] Using SearchTool for factual question.")
                return "search", question
    
        except json.JSONDecodeError:
            print("[DEBUG] Invalid JSON from LLM, defaulting to SearchTool")
    
        # Fallback
        return "search", question

    def run(self, question: str):
        tool_name, expr_or_query = self.decide_tool_and_expr(question)
        tool = self.tools[tool_name]
        if tool_name == "calculator":
            # Support pi in expressions
            expr_or_query = expr_or_query.replace("pi", str(math.pi))
        result = tool.execute(expr_or_query)
        return result
