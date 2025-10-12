import re
from tools import CalculatorTool, SearchTool
from prompt_manager import PromptManager
from hf_llm import LocalLLM


class Agent:
    def __init__(self, classifier_model="mistralai/Mistral-7B-Instruct-v0.2",
                 math_model="Qwen/Qwen2.5-Math-1.5B-Instruct", serpapi_key=None):
        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool(serpapi_key)
        }

        print("[INFO] Loading classifier (Mistral)...")
        self.classifier_llm = LocalLLM(model_name=classifier_model)

        print("[INFO] Loading math reasoning model (Qwen)...")
        self.math_llm = LocalLLM(model_name=math_model)

    def decide_tool_and_expr(self, question: str):
        """
        Decide which tool to use (math/search) and extract a valid expression
        for math questions.
        """

        # Step 1: classify the question
        classification = self.classifier_model.generate(f"Classify the question as 'math' or 'factual': {question}")
        classification = classification.lower().strip()
        print(f"[DEBUG] Mistral classification: {classification}")

        # Step 2: If factual, return search tool
        if "factual" in classification or "fact" in classification:
            return "search", None

        # Step 3: If math, extract expression using Qwen
        qwen_output = self.math_model.generate(
            f"Extract only the clean Python-style mathematical expression from this question: {question}"
        )
        print(f"[DEBUG] Raw Qwen output: {qwen_output!r}")

        # Step 4: Clean the expression
        # Remove markdown, code blocks, explanations, etc.
        expr = qwen_output
        expr = re.sub(r"```.*?```", "", expr, flags=re.S)
        expr = re.sub(r"[^\d\+\-\*\/\%\.\(\)\s]", "", expr)  # allow only math-safe chars
        expr = expr.strip()

        # Fix over-generation like '2+3.232+3'
        expr = re.sub(r"(\d)\.(\d)", r"\1.\2", expr)  # preserve decimals
        expr = re.sub(r"\.\d+\.", ".", expr)  # remove double dots
        expr = re.sub(r"\s+", "", expr)  # remove spaces

        print(f"[DEBUG] Cleaned expression: '{expr}'")

        # Validate expression
        if not re.fullmatch(r"^[\d\+\-\*\/\%\.\(\)]+$", expr):
            print("[ERROR] Invalid expression format")
            return "error", None

        # Step 5: Return to calculator
        return "calculator", expr


    def run(self, question: str) -> str:
        tool_name, expr = self.decide_tool_and_expr(question)

        if tool_name == "calculator":
            if expr:
                print(f"[DEBUG] Sending to CalculatorTool: {expr}")
                return self.tools["calculator"].run(expr)
            return "Calculator: Unable to parse expression"

        if tool_name == "search":
            return self.tools["search"].run(question)

        return "Unable to handle question"
