import re
from tools import CalculatorTool, SearchTool
from hf_llm import LocalLLM
import json
import math

class Agent:
    def __init__(self, llm_model=None, serpapi_key=None):
        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool(serpapi_key)
        }
        self.llm = LocalLLM(model_name=llm_model)

    def decide_tool_and_expr(self, question: str):
        """
        Decide which tool to call based on the question.
        Returns: (tool_name, expression)
        """
    
        simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
        if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
            print(f"[DEBUG] Detected simple numeric expression: {question}")
            return "calculator", question
    
        prompt = f"""
    Classify the question as 'math' or 'factual'.
    Understand the question properly. If it is math, then think step by step and try to give correct expression. Do not give explanation with the JSON format. You should only give JSON format
    Respond ONLY in JSON format like:
    
    {{"type": "math", "expression": "(2+3)*5"}}
    (Examples:
      1) Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May? then provide
        {{"type": "math", "expression": "48+(48/2)"}}
      2) Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn? then provide
         {{"type": "math", "expression": "(12/60)*50"}}
      3) Julie is reading a 120-page book. Yesterday, she was able to read 12 pages and today, she read twice as many pages as yesterday. 
         If she wants to read half of the remaining pages tomorrow, how many pages should she read? then provide
         {{"type": "math", "expression": "120-(12+(12*2))"}}
    )
    or
    {{"type": "factual", "expression": null}}
    (Examples:
      1) Who is President of America? then provide
         {{"type": "factual", "expression": null}}
      2) What is the currency of India? then provide
         {{"type": "factual", "expression": null}}
      3)  What is the synonym of happy? then provide
         {{"type": "factual", "expression": null}}
    )
    
    Q: {question}
    A:
    """
        response = self.llm.generate(prompt, max_new_tokens=64).strip()
        print(f"[DEBUG] LLM response: {response}")
    
        try:
            parsed = json.loads(response)
    
            if parsed["type"] == "math" and parsed["expression"]:
                expr = parsed["expression"].strip()
                if re.fullmatch(r"^[\d\s\.\+\-\*/\(\)]+$", expr):
                    print(f"[DEBUG] Using CalculatorTool for expression: {expr}")
                    return "calculator", expr
                else:
                    print(f"[DEBUG] Expression invalid or unsafe: {expr}")
                    return "search", question  
    
            elif parsed["type"] == "factual":
                print("[DEBUG] Using SearchTool for factual question.")
                return "search", question
    
            else:
                print("[DEBUG] Unrecognized type, defaulting to SearchTool.")
                return "search", question
    
        except json.JSONDecodeError:
            print("[DEBUG] Invalid JSON from LLM, defaulting to SearchTool")
            return "search", question
    

    def run(self, question: str):
        tool_name, expr_or_query = self.decide_tool_and_expr(question)
        tool = self.tools[tool_name]
        if tool_name == "calculator":
            # Support pi in expressions
            expr_or_query = expr_or_query.replace("pi", str(math.pi))
        result = tool.execute(expr_or_query)
        return result
