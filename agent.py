import re
from tools import CalculatorTool, SearchTool
from prompt_manager import PromptManager
from hf_local_llm import LocalLLM

class Agent:
    def __init__(self, llm_model=None, token=None):
        self.tools = {"calculator": CalculatorTool(), "search": SearchTool()}
        self.llm = LocalLLM(model_name=llm_model)

    def decide_tool_and_expr(self, question: str):
        """
        LLM decides the tool AND, if math, returns an arithmetic expression.
        """
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
        response = self.llm.generate(prompt, max_new_tokens=64).strip()
        if response.lower().startswith("math"):
            # Extract expression
            expr = response.split(",", 1)[-1].strip()
            return "calculator", expr
        else:
            return "search", None

    def run(self, question: str) -> str:
        tool_name, expr = self.decide_tool_and_expr(question)

        if tool_name == "calculator":
            if expr:
                return self.tools["calculator"].run(expr)
            return "Calculator: Unable to parse expression"

        if tool_name == "search":
            return self.tools["search"].run(question)

        return "Unable to handle question"
