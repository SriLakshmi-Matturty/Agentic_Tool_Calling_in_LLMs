import re
import math
import json
from tools import CalculatorTool, SearchTool
from hf_llm import LocalLLM

class Agent:
    def __init__(self, classifier_model=None, math_model=None, serpapi_key=None):
        # Tools
        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool(serpapi_key)
        }
        # LLMs
        self.classifier_llm = LocalLLM(model_name=classifier_model)
        self.math_llm = LocalLLM(model_name=math_model)

    def decide_tool_and_expr(self, question: str):
        """
        Decide which tool to call based on the question.
        Returns: (tool_name, expression_or_query)
        """

        # Step 0: detect simple numeric expressions
        simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
        if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
            print(f"[DEBUG] Simple numeric expression detected: {question}")
            return "calculator", question

        # Step 1: classify question using classifier LLM
        classifier_prompt = f"""
Classify the following question as either 'math' or 'factual'. Respond ONLY with 'math' or 'factual'.

Question: {question}
"""
        classification = self.classifier_llm.generate(classifier_prompt, max_new_tokens=16).strip().lower()
        print(f"[DEBUG] Classifier output: {classification}")

        # Step 2: if math, send to math LLM to extract expression
        if "math" in classification:
            math_prompt = f"""
Extract the correct mathematical expression from the question below.
Respond ONLY in JSON format:
{{"type": "math", "expression": "<expression_here>"}}
Do NOT add explanations.

Question: {question}
"""
            response = self.math_llm.generate(math_prompt, max_new_tokens=128).strip()
            print(f"[DEBUG] Math LLM raw response: {response}")

            try:
                parsed = json.loads(response)
                print(f"[DEBUG] Parsed JSON: {parsed}")
                expr = parsed.get("expression", "").strip()
                if expr:
                    print(f"[DEBUG] Using CalculatorTool for expression: {expr}")
                    return "calculator", expr
                else:
                    print("[DEBUG] Expression missing in JSON, defaulting to search")
                    return "search", question
            except json.JSONDecodeError:
                print("[DEBUG] Invalid JSON from Math LLM, defaulting to search")
                return "search", question

        else:
            # Factual question → use SearchTool
            print("[DEBUG] Using SearchTool for factual question.")
            return "search", question
    
    def run(self, question: str):
        tool_name, expr_or_query = self.decide_tool_and_expr(question)
        tool = self.tools[tool_name]
        if tool_name == "calculator":
            # Support pi in expressions
            expr_or_query = expr_or_query.replace("pi", str(math.pi))
        result = tool.execute(expr_or_query)
        return result
