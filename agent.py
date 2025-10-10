import re
from tools import CalculatorTool, SearchTool
from prompt_manager import PromptManager
from hf_llm import LocalLLM

class Agent:
    def __init__(self, llm_model=None, serpapi_key=None):
        self.tools = {"calculator": CalculatorTool(), "search": SearchTool(serpapi_key)}
        self.llm = LocalLLM(model_name=llm_model)

    def decide_tool_and_expr(self, question: str):
        # 1️⃣ Check if question is simple math
        simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
        if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
            print(f"[DEBUG] Detected simple numeric expression: {question}")
            return "calculator", question

        # 2️⃣ Otherwise, ask LLM to classify & extract expression
        prompt = f"""
Classify the question as 'math' or 'factual'.
If it is math, also provide a valid Python expression for the calculator.
Examples:
Q: Priyansh bought 3 chocolates for $15. Cost for 25?
A: math, 15/3*25

Q: Who is the PM of India?
A: factual

Q: What is 235 * 47?
A: math, 235*47

Q: {question}
A:
"""
        response = self.llm.generate(prompt, max_new_tokens=128).strip()
        print(f"[DEBUG] LLM response: {response}")

        # Attempt to parse
        if "math" in response.lower():
            # extract expression after comma
            if "," in response:
                expr = response.split(",", 1)[-1].strip()
                print(f"[DEBUG] Extracted expression: {expr}")
                return "calculator", expr
            else:
                # fallback: try to extract digits and operators
                expr = "".join(re.findall(r"[\d\.\+\-\*/\(\)]+", response))
                print(f"[DEBUG] Fallback extracted expression: {expr}")
                return "calculator", expr

        # Otherwise, treat as factual
        print("[DEBUG] Using SearchTool for factual question.")
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
