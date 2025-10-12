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
        """Use Mistral to classify; if math, use Qwen to extract expression."""

        # Simple numeric expression quick check
        simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
        if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
            print(f"[DEBUG] Detected simple numeric expression: {question}")
            return "calculator", question

        # 1️⃣ Step: Ask Mistral whether it's math or factual
        classify_prompt = (
            "Classify the following question as 'math' or 'factual'.\n"
            "If it is math, only write 'math'. If factual, only write 'factual'.\n\n"
            f"Q: {question}\nA:"
        )
        classification = self.classifier_llm.generate(classify_prompt, max_new_tokens=10).strip().lower()
        print(f"[DEBUG] Mistral classification: {classification}")

        if "math" in classification:
            # 2️⃣ Step: Ask Qwen to extract the mathematical expression
            expression_prompt = f"""
You are a math reasoning assistant. Convert the following natural language question
into a valid Python-style mathematical expression without calculating the result.

Example conversions:
1) What is 2 plus 3? → 2+3
2) A pen costs 10 and a notebook costs 20. Total cost? → 10+20
3) Natalia sold 48 clips to her friends and half as many more. Total clips? → 48+(48/2)
4) A worker earns $15/hour and works 40 minutes. Earnings? → (15/60)*40

Now convert this question:
{question}
Return ONLY the expression, nothing else.
"""
            expr = self.math_llm.generate(expression_prompt, max_new_tokens=64).strip()
            expr = re.sub(r"[^0-9\+\-\*/\.\(\)\s]", "", expr)  # keep only valid symbols
            print(f"[DEBUG] Qwen extracted expression: {expr}")
            return "calculator", expr if expr else None

        print("[DEBUG] Classified as factual → using SearchTool.")
        return "search", None

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
