# agent.py
# agent.py
import re
from tools import Calculator, DuckDuckGoSearch
from hf_llm import HFLLM  # optional: used only if use_llm_for_fallback=True

class Agent:
    def __init__(self, use_llm_for_fallback=False, llm_model="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        self.tools = {
            "calculator": Calculator(),
            "search": DuckDuckGoSearch()
        }
        self.use_llm_for_fallback = use_llm_for_fallback
        if use_llm_for_fallback:
            self.llm = HFLLM(model_name=llm_model)
        else:
            self.llm = None

    def decide_tool(self, question: str) -> str:
        q = question.lower()
        # If explicit arithmetic operators or words indicating calculation
        if re.search(r'[\+\-\*/\^]', q) or re.search(r'\b(calculate|compute|evaluate|sum|how many|how much|cost|price|paid)\b', q):
            return "calculator"
        # Minutes/hours or currency + numbers often require math
        if re.search(r'\b(minutes|minute|hours|hour|\$|dollars|rupees)\b', q):
            if re.search(r'\d', q):
                return "calculator"
        # otherwise do a web search
        return "search"

    def run(self, question: str) -> str:
        tool_name = self.decide_tool(question)
        tool = self.tools[tool_name]
        print(f"🧩 Using tool: {tool_name}")

        tool_result = tool.run(question)
        print(f"🔍 Tool result: {tool_result}")

        # If search: return tool_result directly if it's a clear sentence
        if tool_name == "search":
            if tool_result.startswith("Search Error") or tool_result.startswith("No clear answer"):
                # fallback to LLM if configured
                if self.use_llm_for_fallback and self.llm:
                    prompt = (
                        f"Search output was ambiguous or empty:\n\n{tool_result}\n\n"
                        f"Question: {question}\n\n"
                        "Using the (possibly noisy) search output, produce a concise accurate answer (one sentence)."
                    )
                    ans = self.llm.generate(prompt, max_new_tokens=60)
                    return ans.strip()
                return tool_result
            # already concise one-sentence; return directly
            return tool_result

        # If calculator: return result or try LLM fallback to produce expression
        if tool_name == "calculator":
            if tool_result.startswith("Calculator Error"):
                if self.use_llm_for_fallback and self.llm:
                    # ask LLM for a single-line Python expression
                    prompt = (
                        f"Rewrite the following question as a single Python arithmetic expression only (no words):\n\n"
                        f"{question}\n\nExpression:"
                    )
                    expr = self.llm.generate(prompt, max_new_tokens=40).splitlines()[0].strip()
                    expr = expr.replace('^', '**')
                    # evaluate using Calculator tool to keep safety
                    eval_result = self.tools["calculator"].run(expr)
                    return eval_result
                return tool_result
            return tool_result

        return "Unhandled tool path."
