import requests

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
        self.api_key = serpapi_key

    def execute(self, query: str) -> str:
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": 3,
            }
            r = requests.get(url, params=params).json()
            snippets = []
            for res in r.get("organic_results", []):
                snippet = res.get("snippet")
                if snippet:
                    snippets.append(snippet)
            if not snippets:
                return "No result found"
            return "\n".join(snippets)
        except Exception as e:
            return f"Search Error: {e}"
