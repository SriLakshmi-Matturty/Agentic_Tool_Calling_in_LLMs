import requests
import sympy as sp

class CalculatorTool:
    name = "calculator"
    description = "Execute simple and complex math calculations using Python/Sympy."

    def run(self, query: str):
        try:
            # Try safe sympy evaluation first
            expr = sp.sympify(query)
            result = expr.evalf()
            return str(result)
        except Exception:
            try:
                # Fallback: Python eval
                return str(eval(query))
            except Exception as e:
                return f"Error: {e}"


class SearchTool:
    name = "search"
    description = "Query factual information from Wikipedia."

    def run(self, query: str):
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
            res = requests.get(url).json()
            if "extract" in res:
                return res["extract"]
            else:
                return "No result found"
        except Exception as e:
            return f"Error: {e}"


class KnowledgeBaseTool:
    name = "knowledge_base"
    description = "Lookup from a local or custom knowledge base (placeholder)."

    def run(self, query: str):
        return f"No custom KB implemented yet. Query was: {query}"
