import re

class CalculatorTool:
    def run(self, query: str) -> str:
        try:
            # Handle "X items for Y$" → unit rate
            match = re.match(r"(\d+)\s+\w+\s+for\s+(\d+)\$", query.lower())
            if match:
                qty, price = map(int, match.groups())
                return f"{price/qty:.2f} per item"
            return str(eval(query, {}, {}))
        except Exception as e:
            return f"Calculator Error: {e}"

class SearchTool:
    def run(self, query: str) -> str:
        q = query.lower()
        if "president of france" in q:
            return "Emmanuel Macron"
        if "president of india" in q:
            return "Droupadi Murmu"
        return f"(Mock Search) No search results for '{query}'"

class KnowledgeBaseTool:
    def run(self, query: str) -> str:
        kb = {
            "capital of france": "Paris",
            "capital of india": "New Delhi",
            "einstein's theory": "Theory of Relativity"
        }
        return kb.get(query.lower(), f"No knowledge found for '{query}'")

class Toolset(dict):
    def __init__(self):
        super().__init__({
            "calculator": CalculatorTool(),
            "search": SearchTool(),
            "knowledge_base": KnowledgeBaseTool(),
        })
