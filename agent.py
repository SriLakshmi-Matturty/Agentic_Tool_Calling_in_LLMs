import re
from tools import CalculatorTool, SearchTool
from prompt_manager import PromptManager
from hf_llm import LocalLLM

class Agent:
    def __init__(self, llm_model=None, serpapi_key=None):
        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool(serpapi_key)
        }
        self.llm = LocalLLM(model_name=llm_model)

    def decide_tool_and_expr(self, question: str):
       
        simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
        if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
            print(f"[DEBUG] Detected simple numeric expression: {question}")
            return "calculator", question

        prompt = f"""
Classify the question as 'math' or 'factual'. If it is factual then do not provide anything.
If it is math, only provide a valid Python expression for the calculator, do not calculate answer just give the regular expression only
(Example: If the question is "What is 2*3?" then provide the expression as 2*3).
Do NOT generate extra questions or examples. Only give expression for the math question do not add extra questions to it.

Q: {question}
A:"""

        response = self.llm.generate(prompt, max_new_tokens=64).strip()
        print(f"[DEBUG] LLM response: {response}")

        if "math" in response.lower():
            expr_match = re.search(r"[\d\.\+\-\*/\(\)\s]+", response)
            if expr_match:
                expr = expr_match.group().strip()
                print(f"[DEBUG] Extracted expression: {expr}")
                return "calculator", expr

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
