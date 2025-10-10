import re
from tools import CalculatorTool, SearchTool
from prompt_manager import PromptManager
from hf_llm import LocalLLM

class Agent:
    def __init__(self, llm_model=None):
        self.tools = {"calculator": CalculatorTool(), "search": SearchTool()}
        self.llm = LocalLLM(model_name=llm_model)

    def decide_tool_and_expr(self, question: str):
        """
        LLM decides the tool AND, if math, returns an arithmetic expression.
        Automatically handles noisy outputs and biases toward calculator for numeric questions.
        """
        # Quick heuristic: if numbers are present, bias toward math
        if re.search(r"\d", question):
            bias_hint = "(Hint: likely math question since it contains numbers.)"
        else:
            bias_hint = ""
    
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
    
    {bias_hint}
    
    Q: {question}
    A:
    """
    
        response = self.llm.generate(prompt, max_new_tokens=64).strip()
    
        # Normalize response
        response_lower = response.lower()
    
        if response_lower.startswith("math"):
            # Extract expression after the first comma
            expr = response.split(",", 1)[-1].strip()
    
            # Clean expression — remove everything except safe math symbols and digits
            expr = re.sub(r"[^0-9+\-*/().]", "", expr)
    
            # Handle accidental empty expressions
            if not expr:
                expr = "0"
            print(expr)
            return "calculator", expr
    
        # Default fallback
        return "search", None


    def run(self, question: str) -> str:
    tool_name, expr = self.decide_tool_and_expr(question)

    if tool_name == "calculator":
        if expr:
            print(f"[DEBUG] Expression passed to calculator: {expr}")
            return self.tools["calculator"].run(expr)
        print("[DEBUG] No valid expression extracted for calculator.")
        return "Calculator: Unable to parse expression"

    if tool_name == "search":
        print("[DEBUG] Using SearchTool for factual question.")
        return self.tools["search"].run(question)

    print("[DEBUG] Unable to classify question type.")
    return "Unable to handle question"
