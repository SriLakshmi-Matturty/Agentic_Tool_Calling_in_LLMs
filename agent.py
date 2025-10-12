import re
from tools import CalculatorTool, SearchTool
from prompt_manager import PromptManager
from hf_llm import LocalLLM


class Agent:
    def __init__(self, classifier_model="mistralai/Mistral-7B-Instruct-v0.2",
                 math_model="Qwen/Qwen2.5-Math-1.5B-Instruct", serpapi_key=None):

        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool(serpapi_key)
        }

        print("[INFO] Loading classifier (Mistral)...")
        self.classifier_llm = LocalLLM(model_name=classifier_model)

        print("[INFO] Loading math reasoning model (Qwen)...")
        self.math_llm = LocalLLM(model_name=math_model)


    def decide_tool_and_expr(self, question: str):
        """
        Decide which tool to use (math/search) and extract a valid expression
        for math questions.
        """
    
        # Step 1: classify using Mistral
        classification = self.classifier_llm.generate(
            f"Classify the following question strictly as either 'math' or 'factual'. Do not give any explanation other than one word 'math' or 'factual': {question}"
        )
        classification = classification.lower().strip()
        print(f"[DEBUG] Mistral classification: {classification}")
    
        # Step 2: if factual, return SearchTool
        if "factual" in classification or "fact" in classification:
            return "search", None
    
        # Step 3: use Qwen to extract expression
        qwen_output = self.math_llm.generate(
            f"Extract ONLY the valid Python-style math expression (no words, no explanation) from this question: {question}"
        )
        print(f"[DEBUG] Raw Qwen output: {qwen_output!r}")
    
        text = qwen_output or ""
    
       
        expr = None
    
        
        boxed_match = re.search(r"\\boxed\{([^}]*)\}", text)
        if boxed_match:
            expr = boxed_match.group(1).strip()
    
        
        if not expr:
            code_match = re.search(r"```(.*?)```", text, flags=re.S)
            if code_match:
                expr = code_match.group(1).strip()
        if not expr:
            backtick_match = re.search(r"`([^`]+)`", text)
            if backtick_match:
                expr = backtick_match.group(1).strip()
    
        if not expr:
            cleaned = re.sub(r"[^0-9\+\-\*\/\%\.\(\)]", " ", text)
            candidates = re.findall(r"[\d\.\+\-\*/\%\(\)]+", cleaned)
            expr = max(candidates, key=len).strip() if candidates else ""
    
        
        expr = re.sub(r"\s+", "", expr)
        expr = re.sub(r"\.\.+", ".", expr)
        print(f"[DEBUG] Final extracted expression: '{expr}'")
    
        if not expr or not re.fullmatch(r"^[\d\.\+\-\*/\%\(\)]+$", expr):
            print("[ERROR] Invalid or empty expression")
            return "error", None
    
        return "calculator", expr


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
