import re
from tools import CalculatorTool, SearchTool
from prompt_manager import PromptManager
from hf_llm import LocalLLM

class Agent:
    def __init__(self, llm_model=None, serpapi_key=None, hf_token=None):
        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool(serpapi_key)
        }
        self.llm = LocalLLM(model_name=llm_model, hf_token=hf_token)

    def decide_tool_and_expr(self, question: str):
        """
        Uses the LLM to decide whether the question is mathematical or factual.
        If math, extracts a valid Python expression for CalculatorTool.
        """
    
        simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
        if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
            print(f"[DEBUG] Detected simple numeric expression: {question}")
            return "calculator", question
    
        # Stronger reasoning-aware prompt
        prompt = f"""
    You are a precise reasoning assistant that classifies a question as "math" or "factual".
    
    If it is math:
    1. Think step-by-step (internally) about how the quantities relate.
    2. Produce a valid Python expression that represents the correct order of operations.
    3. Use parentheses to make the intended logic explicit (e.g., ((16 - 3) - 4) * 2).
    4. Do NOT compute the result, just generate the expression.
    5. Your final answer MUST be in valid JSON format, nothing else.
    
    Examples:
    Q: What is 2 + 3?
    A: {{
      "type": "math",
      "expression": "2 + 3"
    }}
    
    Q: Janet’s ducks lay 16 eggs per day. She eats three and bakes muffins with four. She sells the rest at $2 per egg. How much does she make?
    A: {{
      "type": "math",
      "expression": "((16 - 3) - 4) * 2"
    }}
    
    Q: Who is the president of India?
    A: {{
      "type": "factual",
      "expression": null
    }}
    
    Q: {question}
    A:
    """
    
        response = self.llm.generate(prompt, max_new_tokens=256).strip()
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
    
                # --- Auto-fix heuristic: if multiple '-' and '*' exist, add grouping ---
                if re.search(r"-.*-", expr) and "*" in expr and "(" not in expr:
                    parts = expr.split("*")
                    left = parts[0].strip()
                    right = "*".join(parts[1:]).strip()
                    expr = f"({left}) * {right}"
    
                print(f"[DEBUG] Extracted expression: {expr}")
                return "calculator", expr
    
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
