# tools.py
import math
import requests
import html
import re

# ---------- Helper functions ----------
def _first_sentence(text: str) -> str:
    text = html.unescape(text or "").strip()
    # remove excessive whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return ""
    # split on sentence end punctuation
    parts = re.split(r'(?<=[.!?])\s+', text)
    first = parts[0].strip()
    if not re.search(r'[.!?]$', first):
        first = first + '.'
    return first

def _strip_html(html_text: str) -> str:
    return re.sub(r'<[^>]+>', '', html_text or '')

# ---------- Calculator Tool ----------
class Calculator:
    name = "calculator"
    description = "Performs basic arithmetic calculations."

    def run(self, query: str) -> str:
        """
        Attempts to evaluate a math expression found in `query`.
        Returns a concise string result or an error message starting with 'Calculator Error:'.
        """
        try:
            q = query.strip()
            # remove currency symbols & commas
            q = re.sub(r'[\$,]', '', q)
            # try to find a simple arithmetic expression (e.g. '17 * 24' or '3+5')
            m = re.search(r'(-?\d+(?:\.\d*)?)\s*([\+\-\*/\^])\s*(-?\d+(?:\.\d*)?)', q)
            if m:
                expr = f"{m.group(1)}{m.group(2)}{m.group(3)}"
                expr = expr.replace('^', '**')
            else:
                # fallback: if the query is plain digits or a short expression
                if re.fullmatch(r'[\d\.\s\+\-\*/\^\(\)]+', q):
                    expr = q.replace('^', '**')
                else:
                    return "Calculator Error: could not find a simple arithmetic expression."

            # safe eval with math functions available
            safe_locals = {k: getattr(math, k) for k in dir(math) if not k.startswith("__")}
            result = eval(expr, {"__builtins__": None}, safe_locals)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return str(result)
        except Exception as e:
            return f"Calculator Error: {e}"

# ---------- DuckDuckGo Search Tool ----------
class DuckDuckGoSearch:
    name = "search"
    description = "Runs a DuckDuckGo Instant Answer query and returns a short factual answer."

    def run(self, query: str) -> str:
        """
        Query DuckDuckGo Instant Answer API and return a short concise answer (one sentence).
        If no clear answer, returns an error-like string starting with 'Search Error:' or 'No clear answer'.
        """
        try:
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            resp = requests.get("https://api.duckduckgo.com/", params=params, timeout=8)
            data = resp.json()

            # Prefer AbstractText (concise direct answer)
            abstract = data.get("AbstractText", "") or ""
            if abstract:
                return _first_sentence(abstract)

            # Fallback: check RelatedTopics (often short text)
            related = data.get("RelatedTopics", [])
            if related:
                # RelatedTopics can be nested; iterate and extract first candidate text
                def _walk_related(items):
                    for item in items:
                        if isinstance(item, dict):
                            text = item.get("Text") or _strip_html(item.get("Result") or "")
                            if text:
                                return text
                            # nested topics
                            if "Topics" in item:
                                nested = _walk_related(item["Topics"])
                                if nested:
                                    return nested
                    return None
                candidate = _walk_related(related)
                if candidate:
                    return _first_sentence(candidate)

            # Fallback to Heading
            heading = data.get("Heading", "")
            if heading:
                return _first_sentence(heading)

            return "No clear answer found."
        except Exception as e:
            return f"Search Error: {e}"

