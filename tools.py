class CalculatorTool:
    def run(self, query: str) -> str:
        try:
            return str(eval(query, {}, {}))
        except Exception as e:
            return f"Calculator Error: {e}"


class SearchTool:
    def run(self, query: str) -> str:
        # For now, mock search
        if "President of France" in query:
            return "Emmanuel Macron"
        return f"No search results for '{query}'"


class KnowledgeBaseTool:
    def run(self, query: str) -> str:
        kb = {
            "capital of France": "Paris",
            "Einstein's theory": "Theory of Relativity"
        }
        return kb.get(query, f"No knowledge found for '{query}'")

