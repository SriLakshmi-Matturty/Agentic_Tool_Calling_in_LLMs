import math
import requests
import wikipedia
import re

wikipedia.set_lang("en")

class CalculatorTool:
    name = "calculator"

    def run(self, expr: str) -> str:
        try:
            safe_locals = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
            result = eval(expr, {"__builtins__": None}, safe_locals)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return str(result)
        except Exception as e:
            return f"Calculator Error: {e}"

class SearchTool:
    name = "search"

    def run(self, query: str) -> str:
        # Use Wikipedia API as fallback search
        try:
            hits = wikipedia.search(query, results=1)
            if not hits:
                return "No result found"
            summary = wikipedia.summary(hits[0], sentences=3)
            return summary
        except Exception as e:
            return f"Search Error: {e}"
