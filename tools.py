import requests

class CalculatorTool:
    def execute(self, expr: str) -> str:
        try:
            safe_locals = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
            result = eval(expr, {"_builtins_": None}, safe_locals)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return str(result)
        except Exception as e:
            return f"Calculator Error: {e}"


class SearchTool:
    def __init__(self, serpapi_key=None):
        self.api_key = serpapi_key

    def execute(self, query: str) -> str:
         try:
            # Call SerpAPI
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": 3,  # top 3 results
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
            return f"Search Error: {e}"
