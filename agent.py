import re
from tools import CalculatorTool, SearchTool
from prompt_manager import PromptManager
from hf_llm import LocalLLM

class Agent:
    def __init__(self, llm_model=None, serpapi_key=None):
        self.tools = {"calculator": CalculatorTool(), "search": SearchTool(serpapi_key)}
        self.llm = LocalLLM(model_name=llm_model)

    def decide_tool_and_expr(self, question: str):
    simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
    if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
        print(f"[DEBUG] Detected simple numeric expression: {question}")
        return "calculator", question
    prompt = f"""
Classify the question as 'math' or 'factual'.
If it is math, provide a single valid Python expression for the calculator.
Examples:
Q: Priyansh bought 3 chocolates for $15. Cost for 25?
A: 15/3*25

Q: Who is the PM of India?
A: factual

Q: What is 235 * 47?
A: 235*47

Q: {question}
A:
"""
    response = self.llm.generate(prompt, max_new_tokens=128).strip()
    print(f"[DEBUG] LLM response: {response}")

    if "math" in response.lower() or re.search(r"[\d\+\-\*/\(\)]", response):
        # Extract first line with numbers/operators
        lines = response.splitlines()
        for line in lines[::-1]:  
            expr_match = re.search(r"[\d\.\+\-\*/\(\)]+", line)
            if expr_match:
                expr = expr_match.group()
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
