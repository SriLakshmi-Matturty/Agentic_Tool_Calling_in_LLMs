import json
from tools import CalculatorTool, SearchTool
from prompt_manager import PromptManager
from hf_llm import LocalLLM

class Agent:
    def __init__(self, classifier_model=None, math_model=None, serpapi_key=None, use_llm_for_fallback=True):
        """
        Agent orchestrates classification, tool selection, and post-processing.
        """
        self.use_llm_for_fallback = use_llm_for_fallback
        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool(serpapi_key),
        }

        # Load models
        self.classifier_llm = LocalLLM(model_name=classifier_model)
        self.math_llm = LocalLLM(model_name=math_model)
        self.fallback_llm = LocalLLM(model_name=classifier_model) if use_llm_for_fallback else None

    def classify_question(self, question: str) -> str:
        """
        Use the LLM classifier to decide if a question is 'math' or 'factual'.
        Model must return JSON like {"type": "math"} or {"type": "factual"}.
        """
        prompt = f"""
You are a strict question classifier.
Classify the following question into one of two categories:
1. "math" — if the question involves numbers, calculations, equations, or requires symbolic math reasoning.
2. "factual" — if the question asks about people, places, events, definitions, or facts.

Respond ONLY in strict JSON format like this:
{{"type": "math"}} or {{"type": "factual"}}

Examples:
Q: What is 5+7?
A: {{"type": "math"}}

Q: Who is the Prime Minister of India?
A: {{"type": "factual"}}

Q: If a train travels 120 km in 3 hours, what is its speed?
A: {{"type": "math"}}

Question: {question}
Answer:
"""
        response = self.classifier_llm.generate(prompt, max_new_tokens=50)
        print(f"[DEBUG] Raw classifier output: {response}")

        try:
            parsed = json.loads(response.strip())
            qtype = parsed.get("type", "").lower()
            if qtype in ["math", "factual"]:
                return qtype
        except Exception:
            pass

        # If JSON parsing fails or output invalid
        print("[WARN] Invalid JSON classification output. Falling back to keyword logic.")
        lower_q = question.lower()
        if any(ch.isdigit() for ch in lower_q) or any(w in lower_q for w in ["sum", "multiply", "add", "divide", "area", "value", "solve", "x", "y"]):
            return "math"
        return "factual"

    def extract_math_expression(self, question: str) -> str:
        """
        Ask the math LLM to extract the symbolic expression.
        """
        prompt = f"""
You are a math expression extractor.

Instructions:
1. Respond ONLY with a JSON object containing a symbolic expression.
2. The JSON must have ONLY one key: "expression".
   Example: {{"expression": "2+3"}}
3. DO NOT compute the answer.
4. DO NOT include explanations, reasoning, code, "result", or "=".
5. Use only +, -, *, /, parentheses, pi, numbers, and variables.

Question: {question}
Answer:
"""
        response = self.math_llm.generate(prompt, max_new_tokens=150)
        print(f"[DEBUG] Math LLM raw response: {response}")

        try:
            data = json.loads(response.strip())
            expr = data.get("expression", "").strip()
            if expr:
                return expr
        except Exception:
            pass
        print("[WARN] Could not extract expression properly. Returning empty.")
        return ""

    def run(self, question: str):
        """
        Main agent execution.
        """
        print(f"[INFO] Processing question: {question}")
        qtype = self.classify_question(question)
        print(f"[DEBUG] Classified as: {qtype}")

        if qtype == "math":
            expr = self.extract_math_expression(question)
            print(f"[DEBUG] Extracted expression: {expr}")
            if expr:
                print(f"[DEBUG] Using CalculatorTool from JSON expression: {expr}")
                result = self.tools["calculator"].run(expr)
                print(f"[DEBUG] Tool selected: calculator, expr/query: {expr}")
                print(f"[DEBUG] Tool result: {result}")
                return result
            else:
                print("[WARN] No valid expression extracted. Falling back to LLM for final answer.")
                return self.math_llm.generate(question, max_new_tokens=100)

        elif qtype == "factual":
            print(f"[DEBUG] Tool selected: search, query: {question}")
            result = self.tools["search"].run(question)
            print(f"[DEBUG] Tool result: {result}")
            if self.use_llm_for_fallback and self.fallback_llm:
                prompt = PromptManager.build_final_prompt(question, result)
                print("[DEBUG] Using fallback LLM for post-processing factual answer.")
                return self.fallback_llm.generate(prompt, max_new_tokens=200)
            return result

        else:
            print(f"[WARN] Unknown classification '{qtype}', defaulting to factual search.")
            return self.tools["search"].run(question)
