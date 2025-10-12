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
        """Classify with Mistral; extract expression with Qwen; sanitize & validate strictly."""

        simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
        if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
            print(f"[DEBUG] Detected simple numeric expression: {question}")
            return "calculator", question

        # 1️⃣ Step: Classification using Mistral
        classify_prompt = (
            "Classify the following question as 'math' or 'factual'.\n"
            "If it is math, only write 'math'. If factual, only write 'factual'.\n\n"
            f"Q: {question}\nA:"
        )
        classification = self.classifier_llm.generate(classify_prompt, max_new_tokens=10).strip().lower()
        print(f"[DEBUG] Mistral classification: {classification}")

        # If it's a math question
        if "math" in classification:
            # 2️⃣ Step: Extract math expression via Qwen
            expression_prompt = f"""
You are a math reasoning assistant. Convert this question into a valid Python mathematical expression (without units or $ signs).

Examples:
- What is 2 plus 3? → 2+3
- A pen costs 10 and a notebook costs 20. Total cost? → 10+20
- Natalia sold 48 clips and half as many more. Total clips? → 48+(48/2)
- A worker earns $15/hour and works 40 minutes. Earnings? → (15/60)*40
- Priyansh bought 3 chocolates for $15. Cost for 25? → (15/3)*25

Now convert:
{question}
Return ONLY the expression, nothing else.
"""
            raw_expr = self.math_llm.generate(expression_prompt, max_new_tokens=64).strip()
            print(f"[DEBUG] Raw Qwen output: {repr(raw_expr)}")

            # 3️⃣ Step: Clean expression aggressively
            expr = raw_expr
            expr = expr.replace("$", "")  # remove currency symbols
            expr = re.sub(r"[^0-9\+\-\*/\.\(\)]", "", expr)  # remove all non-math chars
            expr = re.sub(r"\.{2,}", ".", expr)  # collapse multiple dots
            expr = re.sub(r"^\.+|\.+$", "", expr)  # trim leading/trailing dots
            print(f"[DEBUG] Cleaned expression: {repr(expr)}")

            # 4️⃣ Step: Validate strictly
            valid_expr_pattern = r"^[\d\.\+\-\*/\(\)]+$"
            if not expr or not re.fullmatch(valid_expr_pattern, expr):
                print("[WARN] Invalid or nonsensical math expression. Switching to SearchTool.")
                return "search", None

            return "calculator", expr

        # 5️⃣ Default factual
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
