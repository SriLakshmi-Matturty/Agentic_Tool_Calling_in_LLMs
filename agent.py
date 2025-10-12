import re, json, math
from tools import CalculatorTool, SearchTool
from hf_llm import LocalLLM

class Agent:
    def __init__(self, classifier_model=None, math_model=None, serpapi_key=None):
        # Tools
        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool(serpapi_key)
        }
        # LLMs
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
        # Quick numeric check
        if re.fullmatch(r"^[\d\s\.\+\-\*/\(\)]+$", question.replace(" ", "")):
            print(f"[DEBUG] Simple numeric expression detected: {question}")
            return "calculator", question
    
        # Classify

        # classify using LLM
        classifier_prompt = f"""
        Classify the following question as 'math' or 'factual'.
        Return ONLY a JSON object like: {{"type": "math"}} or {{"type": "factual"}}.
        Do NOT include any explanations or extra text. Please please only give JSON format.
        (Example: If the question is 
         1) What is 2+3? then output {{"type": "math"}}
         2) Julie is reading a 120-page book. Yesterday, she was able to read 12 pages and today, she read twice as many pages as yesterday.
            If she wants to read half of the remaining pages tomorrow, how many pages should she read? then output {{"type": "math"}}
        3) Who is President of America? then output {{"type": "factual"}}
        4) What is the capital of Australia? then output {{"type": "factual"}}
       ).
       Please only give this format. Do not add anything before that JSON format. This prompt is to guide you. Do not give include this in output. Only give JSON output.
        Question: {question}
        """
        
        raw_class = self.classifier_llm.generate(classifier_prompt, max_new_tokens=16).strip()
        print(f"[DEBUG] Classifier raw output: {raw_class}")
        
        # Extract JSON
        try:
            parsed = json.loads(raw_class)
            classification = parsed.get("type", "factual").lower()
        except:
            classification = "factual"  # fallback
        
        print(f"[DEBUG] Classifier final: {classification}")

    
        if classification == "math.":
            # Math LLM prompt with explicit JSON enforcement
            math_prompt = f"""
    Return ONLY a JSON object with key "expression".
    Do NOT include explanations, reasoning, or any extra text.
    Use only numbers, +, -, *, /, parentheses, and pi.
    
    Example:
    Q: What is 2+3?
    A: {{"expression": "2+3"}}
    
    Question: {question}
    """
            resp = self.math_llm.generate(math_prompt, max_new_tokens=128).strip()
            print(f"[DEBUG] Math LLM raw response: {resp}")
    
            # Extract last JSON object from text
            json_matches = re.findall(r"\{.*?\}", resp, re.DOTALL)
            parsed = None
            if json_matches:
                for jm in reversed(json_matches):
                    try:
                        parsed = json.loads(jm)
                        if "expression" in parsed:
                            break
                    except:
                        continue
    
            if parsed and "expression" in parsed:
                expr = self.clean_expression(parsed["expression"])
                print(f"[DEBUG] Using CalculatorTool from JSON expression: {expr}")
                return "calculator", expr
    
            # Regex fallback (digits, operators, parentheses, pi)
            print("[DEBUG] Could not extract JSON, trying regex fallback")
            expr = self.extract_expression_from_text(resp)
            if expr:
                # Strip unmatched parentheses
                open_par = expr.count("(")
                close_par = expr.count(")")
                if open_par > close_par:
                    expr += ")" * (open_par - close_par)
                expr = self.clean_expression(expr)
                print(f"[DEBUG] Using CalculatorTool from regex extracted expression: {expr}")
                return "calculator", expr
    
            print("[DEBUG] Fallback to SearchTool")
            return "search", question
    
        else:
            print("[DEBUG] Using SearchTool for factual question.")
            return "search", question

    # ---------- optional summarizer for search ----------
    def summarize_search(self, question: str, context: str) -> str:
        prompt = f"""
Extract only short factual answer(s) for the question below, in a concise comma-separated list.
Do NOT include explanations or long text.

Question: {question}
Context: {context}
"""
        return self.classifier_llm.generate(prompt, max_new_tokens=64).strip()

    # ---------- run ----------
    def run(self, question: str):
        print(f"[INFO] Processing question: {question}")

        # Decide tool
        tool_name, expr_or_query = self.decide_tool_and_expr(question)
        print(f"[DEBUG] Tool selected: {tool_name}, expr/query: {expr_or_query}")

        # Execute
        tool = self.tools[tool_name]
        if tool_name == "calculator":
            expr_or_query = expr_or_query.replace("pi", str(math.pi))

        result = tool.execute(expr_or_query)
        print(f"[DEBUG] Tool result: {result}")

        # Summarize if search
        if tool_name == "search":
            summarized = self.summarize_search(question, result)
            print(f"[DEBUG] Summarized Search Result: {summarized}")
            return summarized or result

        return result
