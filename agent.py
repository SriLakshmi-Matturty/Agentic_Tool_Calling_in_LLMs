import re
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

    # ------------------------ Helper Methods ------------------------

    def extract_expression_from_text(self, text: str) -> str:
        """Extracts arithmetic expression safely from text."""
        pattern = r"[0-9\+\-\*/\.\(\)pi ]+"
        matches = re.findall(pattern, text)
        if matches:
            return max(matches, key=len).strip()
        return None

    def extract_json_from_text(self, text: str):
        """Extract JSON object from LLM output."""
        match = re.search(r'\{.*?\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return None
        return None

    def clean_expression(self, expr: str) -> str:
        """Cleans extra symbols or spaces from expression."""
        expr = expr.strip()
        if expr.endswith('='):
            expr = expr[:-1].strip()
        return expr

    # ------------------------ Core Logic ------------------------

    def decide_tool_and_expr(self, question: str):
        """Decides which tool to call: calculator or search."""

        # Step 0: Detect simple numeric expressions like "2+3"
        simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
        if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
            print(f"[DEBUG] Simple numeric expression detected: {question}")
            return "calculator", question

        # Step 1: Classify as math or factual
        classifier_prompt = f"""
You are a classifier that decides if a question is 'math' or 'factual'.
Respond ONLY with one word: "math" or "factual".
Do NOT explain or repeat the question.

Question: {question}
Answer:
"""
        classification = (
            self.classifier_llm.generate(classifier_prompt, max_new_tokens=8)
            .strip()
            .lower()
        )

        # Force sanitize LLM output
        classification = "math" if "math" in classification else "factual"
        print(f"[DEBUG] Classifier final decision: {classification}")

        # Step 2: If math → extract symbolic expression
        if classification == "math":
            math_prompt = f"""
You are a math expression extractor.

Rules:
- Respond ONLY with a JSON object containing one key: "expression".
- Do NOT compute the answer or include explanations.
- Use only +, -, *, /, parentheses, pi, numbers, and variables.

Example:
Q: What is 2+3?
A: {{"expression": "2+3"}}

Q: Julie read 12 pages yesterday, today twice as many, half remaining tomorrow?
A: {{"expression": "120-(12+12*2)/2"}}

Question: {question}
Answer:
"""
            response = self.math_llm.generate(math_prompt, max_new_tokens=128).strip()
            print(f"[DEBUG] Math LLM raw response: {response}")

            parsed = self.extract_json_from_text(response)
            if parsed and "expression" in parsed:
                expr = self.clean_expression(parsed["expression"])
                print(f"[DEBUG] Extracted expression: {expr}")
                return "calculator", expr

            # Fallback to regex
            expr = self.extract_expression_from_text(response)
            if expr:
                expr = self.clean_expression(expr)
                print(f"[DEBUG] Fallback extracted expression: {expr}")
                return "calculator", expr

            # If nothing works
            print("[DEBUG] Could not extract expression, defaulting to SearchTool")
            return "search", question

        # Step 3: Factual → use SearchTool
        print("[DEBUG] Classified as factual → using SearchTool")
        return "search", question

    # ------------------------ Postprocessing ------------------------

    def summarize_search(self, question: str, context: str) -> str:
        """Summarizes search results concisely."""
        prompt = f"""
Provide a short, direct factual answer for the question below.
No explanations or long text — just the key fact(s) in a comma-separated list.

Question: {question}
Context: {context}

Example:
Q: What do Jamaican people speak?
A: Jamaican Patois, English
"""
        return self.classifier_llm.generate(prompt, max_new_tokens=64).strip()

    # ------------------------ Main Execution ------------------------

    def run(self, question: str):
        print(f"[INFO] Processing question: {question}")

        tool_name, expr_or_query = self.decide_tool_and_expr(question)
        print(f"[DEBUG] Tool selected: {tool_name}, expr/query: {expr_or_query}")

        result = self.tools[tool_name].execute(expr_or_query)
        print(f"[DEBUG] Tool result: {result}")

        if tool_name == "search":
            summarized = self.summarize_search(question, result)
            print(f"[DEBUG] Summarized Search Result: {summarized}")
            return summarized or result

        return result
