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
        classification = self.classifier_llm.generate(
            f"Classify the following question strictly as either 'math' or 'factual': {question}"
        )
        classification = classification.lower().strip()
        print(f"[DEBUG] Mistral classification: {classification}")

        # Step 2: factual → Search Tool
        if "factual" in classification or "fact" in classification:
            return "search", None

        # Step 3: math → Qwen for expression extraction
        qwen_output = self.math_llm.generate(
            f"Extract ONLY the valid Python-style math expression (no words) from this question: {question}"
        )
        print(f"[DEBUG] Raw Qwen output: {qwen_output!r}")

        # Step 4: Clean the expression
        expr = qwen_output or ""
        expr = re.sub(r"```.*?```", "", expr, flags=re.S)   # remove code fences
        expr = re.sub(r"[a-zA-Z=<>]", "", expr)             # remove letters or equality signs
        expr = re.sub(r"[^\d\+\-\*\/\%\.\(\)\s]", "", expr) # allow only math chars
        expr = re.sub(r"\s+", "", expr)                     # remove whitespace
        expr = expr.strip()

        # Handle over-generation like “2+3.232+3”
        expr = re.sub(r"\.\.+", ".", expr)
        expr = expr.replace("..", ".")

        print(f"[DEBUG] Cleaned expression: '{expr}'")

        # Step 5: Validate expression
        if not expr or not re.fullmatch(r"^[\d\+\-\*\/\%\.\(\)]+$", expr):
            print("[ERROR] Invalid or empty expression")
            return "error", None

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
