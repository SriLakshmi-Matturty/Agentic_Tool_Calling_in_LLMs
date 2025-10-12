import re
import math
import json
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

    def extract_expression_from_text(self, text: str) -> str:
        """
        Extracts a safe arithmetic expression from raw text if JSON fails.
        Only digits, operators, parentheses, pi, and spaces.
        """
        pattern = r"[0-9\+\-\*/\.\(\)pi ]+"
        matches = re.findall(pattern, text)
        if matches:
            return max(matches, key=len).strip()  # longest match is likely correct
        return None

    def extract_json_from_text(self, text: str):
        """
        Extracts the first JSON object from the LLM output.
        """
        match = re.search(r'\{.*?\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return None
        return None

    def clean_expression(self, expr: str) -> str:
        """
        Cleans the expression by removing trailing '=' and extra spaces.
        """
        expr = expr.strip()
        if expr.endswith('='):
            expr = expr[:-1].strip()
        return expr

    def decide_tool_and_expr(self, question: str):
        """
        Decide which tool to call based on the question.
        Returns: (tool_name, expression_or_query)
        """
        # Step 0: detect simple numeric expressions
        simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
        if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
            print(f"[DEBUG] Simple numeric expression detected: {question}")
            return "calculator", question

        # Step 1: classify question using classifier LLM
        classifier_prompt = f"""
Classify the following question as either 'math' or 'factual'. Do not give any output other than "math" or "factual".
(Examples:
 1) Who is President of America? then give "factual".
 2) What is 17*24? then give "math".
 3) What is AI? then give "factual".
 4) Julie is reading a 120-page book. Yesterday, she was able to read 12 pages and today, she read twice as many pages as yesterday. 
    If she wants to read half of the remaining pages tomorrow, how many pages should she read? then give "math".

Question: {question}
"""
        classification = self.classifier_llm.generate(classifier_prompt, max_new_tokens=16).strip().lower()
        print(f"[DEBUG] Classifier output: {classification}")

        # Step 2: if math, send to math LLM to extract symbolic expression
        if "math" in classification:
            math_prompt = f"""
You are a math expression extractor.

Instructions:
1. Respond ONLY with a JSON object containing a symbolic expression.
2. The JSON must have ONLY one key: "expression".
   Example: {{"expression": "2+3"}}
3. DO NOT compute the answer.
4. DO NOT include explanations, reasoning, code, "result", or "=".
5. Use only +, -, *, /, parentheses, pi, numbers, and variables.

Examples:
Q: What is 2+3?
A: {{"expression": "2+3"}}

Q: Julie read 12 pages yesterday, today twice as many, half remaining tomorrow?
A: {{"expression": "120-(12+12*2)/2"}}

Question: {question}
"""
            response = self.math_llm.generate(math_prompt, max_new_tokens=128).strip()
            print(f"[DEBUG] Math LLM raw response: {response}")

            # Try extracting JSON first
            parsed = self.extract_json_from_text(response)
            if parsed and "expression" in parsed:
                expr = self.clean_expression(parsed["expression"])
                print(f"[DEBUG] Using CalculatorTool from JSON expression: {expr}")
                return "calculator", expr
            else:
                # JSON not found, fallback to regex
                print("[DEBUG] Could not extract JSON, trying regex fallback")
                expr = self.extract_expression_from_text(response)
                if expr:
                    expr = self.clean_expression(expr)
                    print(f"[DEBUG] Using CalculatorTool from regex extracted expression: {expr}")
                    return "calculator", expr

            # If all fails
            print("[DEBUG] Could not extract expression, defaulting to SearchTool")
            return "search", question

        else:
            # Factual question → use SearchTool
            print("[DEBUG] Using SearchTool for factual question.")
            return "search", question

    def summarize_search(self, question: str, context: str) -> str:
        """Summarize long search results using same LLM."""
        prompt = f"""
Extract only the short factual answer(s) for the question below, in a concise comma-separated list.
Do not include explanations or long sentences.

Question: {question}
Context: {context}

Example:
Q: What do Jamaican people speak?
A: Jamaican Patois, English
"""
        return self.classifier_llm.generate(prompt, max_new_tokens=64).strip()

    def run(self, question: str):
        print(f"[INFO] Processing question: {question}")
    
        # Step 1: Decide which tool and what query/expression to use
        tool_name, expr_or_query = self.decide_tool_and_expr(question)
        print(f"[DEBUG] Tool selected: {tool_name}, expr/query: {expr_or_query}")
    
        # Step 2: Execute the chosen tool
        result = self.tools[tool_name].execute(expr_or_query)
        print(f"[DEBUG] Tool result: {result}")
    
        # Step 3: If factual (search), summarize the result using same LLM
        if tool_name == "search":
            summarized = self.summarize_search(question, result)
            print(f"[DEBUG] Summarized Search Result: {summarized}")
            return summarized or result
    
        # Step 4: Otherwise (math/calculator), return the computed result
        return result
