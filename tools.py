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
        if "President of India" in query:
            return "Droupadi Murmu"
        return f"No search results for '{query}'"


class KnowledgeBaseTool:
    def run(self, query: str) -> str:
        kb = {
            "capital of France": "Paris",
            "Einstein's theory": "Theory of Relativity",
            "capital of India": "New Delhi"
        }
        return kb.get(query, f"No knowledge found for '{query}'")


class Toolset(dict):
    def __init__(self):
        super().__init__({
            "calculator": CalculatorTool(),
            "search": SearchTool(),
            "knowledge_base": KnowledgeBaseTool(),
        })

