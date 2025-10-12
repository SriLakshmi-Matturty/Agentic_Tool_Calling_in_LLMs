import requests
from hf_llm import LocalLLM

class CalculatorTool:
    def execute(self, expr: str) -> str:
        try:
            # Safe eval for arithmetic expressions
            allowed_chars = "0123456789+-*/.() "
            if not all(c in allowed_chars for c in expr):
                return "Calculator Error: Invalid characters"
            result = eval(expr)
            return result
        except Exception as e:
            return f"Calculator Error: {e}"


class SearchTool:
    def __init__(self, serpapi_key=None):
        self.serpapi_key = serpapi_key

    def execute(self, query: str):
        """Use SerpAPI to fetch factual snippets only (no summarization)."""
        try:
            url = "https://serpapi.com/search"
            params = {"q": query, "api_key": self.serpapi_key}
            resp = requests.get(url, params=params)
            data = resp.json()

            snippets = []
            if "organic_results" in data:
                for r in data["organic_results"][:5]:
                    if "snippet" in r:
                        snippets.append(r["snippet"])

            text_block = " ".join(snippets)
            return text_block or "No results found."
        except Exception as e:
            return f"Search Error: {str(e)}"
