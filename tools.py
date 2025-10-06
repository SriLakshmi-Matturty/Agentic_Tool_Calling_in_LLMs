import re
import json
import math
import requests
import wikipedia

wikipedia.set_lang("en")

import math

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
    description = "Searches the web using DuckDuckGo API, and falls back to Wikipedia if needed."

    def _duckduckgo_search(self, query: str):
        """Query DuckDuckGo Instant Answer API."""
        try:
            url = "https://api.duckduckgo.com/"
            params = {"q": query, "format": "json", "no_redirect": "1", "no_html": "1"}
            r = requests.get(url, params=params, timeout=8)
            data = r.json()

            # Extract main info
            if data.get("AbstractText"):
                return {
                    "type": "summary",
                    "title": data.get("Heading") or query,
                    "summary": data.get("AbstractText")
                }

            # If it's a person, often in RelatedTopics
            topics = data.get("RelatedTopics", [])
            for t in topics:
                if isinstance(t, dict) and "Text" in t:
                    text = t["Text"]
                    if re.match(r"^[A-Z][a-z]+(\s[A-Z][a-z]+)+", text):
                        return {
                            "type": "person",
                            "name": text.split(" - ")[0],
                            "summary": text
                        }
            return None
        except Exception as e:
            return {"type": "error", "message": f"DuckDuckGo API error: {e}"}

    def _wikipedia_fallback(self, query: str):
        """Fallback search using Wikipedia if DuckDuckGo gives no good answer."""
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

        # Detect “Who is the <role> of <entity>?” type question
        m = re.search(r'who\s+is\s+the\s+(.+?)\s+of\s+([^\?\.]+)', query, flags=re.I)
        if m:
            role = m.group(1).strip()
            entity = m.group(2).strip()
            combined = f"current {role} of {entity}"
            data = self._duckduckgo_search(combined)
            if not data:
                data = self._wikipedia_fallback(combined)
        else:
            # Generic query
            data = self._duckduckgo_search(query)
            if not data:
                data = self._wikipedia_fallback(query)

        return json.dumps(data, ensure_ascii=False)
