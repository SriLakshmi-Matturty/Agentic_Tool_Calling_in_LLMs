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
            return "calculator", question

        # Step 1: classify question using classifier LLM
        classifier_prompt = f"""
        Classify the following question as either 'math' or 'factual'. Respond only with 'math' or 'factual'.

        Question: {question}
        """
        classification = self.classifier_llm.generate(classifier_prompt, max_new_tokens=16).strip().lower()

        # Step 2: if math, send to math LLM to extract expression
        if "math" in classification:
            math_prompt = f"""
            Extract the correct mathematical expression from the question below.
            Respond ONLY in JSON format:
            {{"type": "math", "expression": "<expression_here>"}}
            Do not add explanations.

            Question: {question}
            """
            response = self.math_llm.generate(math_prompt, max_new_tokens=64).strip()

            try:
                parsed = json.loads(response)
                expr = parsed.get("expression", "").strip()
                if expr:
                    return "calculator", expr
                else:
                    return "search", question
            except json.JSONDecodeError:
                # fallback
                return "search", question

        else:
            # Factual question → use SearchTool
            return "search", question

    
    def run(self, question: str):
        tool_name, expr_or_query = self.decide_tool_and_expr(question)
        tool = self.tools[tool_name]
        if tool_name == "calculator":
            # Support pi in expressions
            expr_or_query = expr_or_query.replace("pi", str(math.pi))
        result = tool.execute(expr_or_query)
        return result
