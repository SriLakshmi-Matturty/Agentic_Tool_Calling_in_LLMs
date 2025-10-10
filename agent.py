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
    If it is math, ONLY return a single valid Python expression.
    Do NOT include explanations, comments, or other examples.
    
    Q: {question}
    A:
    """
        response = self.llm.generate(prompt, max_new_tokens=64).strip()
        print(f"[DEBUG] LLM response: {response}")
    
        expr_match = re.search(r"[\d\.\+\-\*/\(\)]+", response)
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
