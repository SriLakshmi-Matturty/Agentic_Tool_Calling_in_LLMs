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
        """
        Uses the LLM to decide whether the question is mathematical or factual.
        If math, extracts a valid Python expression for CalculatorTool.
        """
    
        simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
        if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
            print(f"[DEBUG] Detected simple numeric expression: {question}")
            return "calculator", question
    
        # Stronger prompt with JSON constraint
        prompt = f"""
    You are a classifier that decides whether a question is "math" or "factual".
    
    - If the question requires numeric or arithmetic reasoning, classify it as "math"
      and provide a valid Python expression string that can be evaluated with eval().
    - If the question is factual or conceptual, classify it as "factual" and return None.
    
    ⚠️ Output MUST be in strict JSON format as below:
    {{
      "type": "math",
      "expression": "2 + 3"
    }}
    
    or
    
    {{
      "type": "factual",
      "expression": null
    }}
    
    Do NOT include explanations, examples, or any text outside JSON.
    
    Q: {question}
    A:
    """
    
        response = self.llm.generate(prompt, max_new_tokens=128).strip()
        print(f"[DEBUG] Raw LLM response: {response}")
    
        import json
        try:
            json_text = re.search(r"\{.*\}", response, re.DOTALL)
            if not json_text:
                raise ValueError("No JSON found in response")
    
            data = json.loads(json_text.group())
            q_type = data.get("type", "").lower()
            expr = data.get("expression")
    
            if q_type == "math" and expr:
                expr = expr.strip()
                if re.match(r"^[\d\s\.\+\-\*/\(\)]+$", expr):
                    print(f"[DEBUG] Extracted expression: {expr}")
                    return "calculator", expr
                else:
                    print(f"[DEBUG] Invalid math expression format: {expr}")
                    return "calculator", None
    
            elif q_type == "factual":
                print("[DEBUG] Classified as factual.")
                return "search", None
    
        except Exception as e:
            print(f"[DEBUG] JSON parse error: {e}")
            print("[DEBUG] Defaulting to search.")
            return "search", None
    
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
