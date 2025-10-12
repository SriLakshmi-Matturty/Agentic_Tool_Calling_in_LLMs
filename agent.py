import re, json, math
from tools import CalculatorTool, SearchTool
from hf_llm import LocalLLM

class Agent:
    def _init_(self, classifier_model=None, math_model=None, serpapi_key=None):
        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool(serpapi_key)
        }
        self.classifier_llm = LocalLLM(model_name=classifier_model)
        self.math_llm = LocalLLM(model_name=math_model)

    # ---------- helpers ----------
    def extract_json_from_text(self, text: str):
        match = re.search(r"\{.*?\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return None
        return None

    def extract_expression_from_text(self, text: str):
        pattern = r"[0-9\+\-\*/\.\(\)pi ]+"
        matches = re.findall(pattern, text)
        return max(matches, key=len).strip() if matches else None

    def clean_expression(self, expr: str):
        expr = expr.strip()
        if expr.endswith("="):
            expr = expr[:-1].strip()
        return expr

    # ---------- main logic ----------
    def decide_tool_and_expr(self, question: str):
        # quick numeric check
        if re.fullmatch(r"^[\d\s\.\+\-\*/\(\)]+$", question.replace(" ", "")):
            print(f"[DEBUG] Simple numeric expression detected: {question}")
            return "calculator", question

        # classify
        classifier_prompt = f"Classify as 'math' or 'factual'. Reply with only one word.\nQuestion: {question}"
        classification = self.classifier_llm.generate(classifier_prompt, max_new_tokens=8).strip().lower()
        print(f"[DEBUG] Classifier output: {classification}")

        if "math" in classification:
            math_prompt = f"""
You are a math expression extractor.
Return ONLY a JSON with one key "expression".
Example: {{"expression": "2+3"}}
Do NOT compute or explain.
Question: {question}
"""
            resp = self.math_llm.generate(math_prompt, max_new_tokens=128).strip()
            print(f"[DEBUG] Math LLM raw response: {resp}")

            parsed = self.extract_json_from_text(resp)
            if parsed and "expression" in parsed:
                expr = self.clean_expression(parsed["expression"])
                print(f"[DEBUG] Using CalculatorTool from JSON expression: {expr}")
                return "calculator", expr

            print("[DEBUG] Could not extract JSON, trying regex fallback")
            expr = self.extract_expression_from_text(resp)
            if expr:
                expr = self.clean_expression(expr)
                print(f"[DEBUG] Using CalculatorTool from regex extracted expression: {expr}")
                return "calculator", expr

            print("[DEBUG] Fallback to SearchTool")
            return "search", question
        else:
            print("[DEBUG] Using SearchTool for factual question.")
            return "search", question

    def run(self, question: str):
        tool_name, expr_or_query = self.decide_tool_and_expr(question)
        print(f"[DEBUG] Tool selected: {tool_name}, expr/query: {expr_or_query}")
        tool = self.tools[tool_name]
        if tool_name == "calculator":
            expr_or_query = expr_or_query.replace("pi", str(math.pi))
        result = tool.execute(expr_or_query)
        print(f"[DEBUG] Tool result: {result}")
        return result
