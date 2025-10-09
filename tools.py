import re
import json
import math
import requests
import wikipedia

wikipedia.set_lang("en")

class CalculatorTool:
    name = "calculator"
    description = "Performs safe arithmetic evaluations."

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
    description = "Searches the web using DuckDuckGo API, fallback to Wikipedia."

    def _duckduckgo_search(self, query: str):
        try:
            url = "https://api.duckduckgo.com/"
            params = {"q": query, "format": "json", "no_redirect": "1", "no_html": "1"}
            r = requests.get(url, params=params, timeout=8)
            data = r.json()
            if data.get("AbstractText"):
                return {"type": "summary", "title": data.get("Heading") or query, "summary": data.get("AbstractText")}
            return None
        except:
            return None

    def _wikipedia_fallback(self, query: str):
        try:
            hits = wikipedia.search(query, results=5)
            if not hits:
                return {"type": "error", "message": f"No results for '{query}'"}
            title = hits[0]
            summary = wikipedia.summary(title, sentences=3)
            return {"type": "summary", "title": title, "summary": summary}
        except Exception as e:
            return {"type": "error", "message": f"Wikipedia error: {e}"}

    def run(self, query: str) -> str:
        query = query.strip()
        data = self._duckduckgo_search(query)
        if not data:
            data = self._wikipedia_fallback(query)
        return json.dumps(data, ensure_ascii=False)
