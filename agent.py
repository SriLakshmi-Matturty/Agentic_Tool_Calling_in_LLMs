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

    def extract_expression_from_text(self, text: str) -> str:
        """
        Extracts a safe mathematical expression from raw text if JSON fails.
        Only allows digits, operators, parentheses, pi, and spaces.
        """
        pattern = r"[0-9\+\-\*/\.\(\)pi ]+"
        matches = re.findall(pattern, text)
        if matches:
            # Return the longest match (most likely the intended expression)
            expr = max(matches, key=len)
            return expr.strip()
        return None

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

            # Try JSON parsing first
            try:
                parsed = json.loads(response)
                expr = parsed.get("expression", "").strip()
                if expr:
                    print(f"[DEBUG] Using CalculatorTool from JSON expression: {expr}")
                    return "calculator", expr
            except json.JSONDecodeError:
                print("[DEBUG] JSON parsing failed, trying regex fallback")
                expr = self.extract_expression_from_text(response)
                if expr:
                    print(f"[DEBUG] Using CalculatorTool from regex extracted expression: {expr}")
                    return "calculator", expr

            # If all fails
            print("[DEBUG] Could not extract expression, defaulting to SearchTool")
            return "search", question

        else:
            # Factual question → use SearchTool
            print("[DEBUG] Using SearchTool for factual question.")
            return "search", question

    def run(self, question: str):
        tool_name, expr_or_query = self.decide_tool_and_expr(question)
        print(f"[DEBUG] Tool selected: {tool_name}, expr/query: {expr_or_query}")
        tool = self.tools[tool_name]

        # Support pi in expressions
        if tool_name == "calculator":
            expr_or_query = expr_or_query.replace("pi", str(math.pi))

        result = tool.execute(expr_or_query)
        print(f"[DEBUG] Tool result: {result}")
        return result
