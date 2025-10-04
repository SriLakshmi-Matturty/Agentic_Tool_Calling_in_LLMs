#tools.py
import wikipedia

class CalculatorTool:
    def run(self, query: str) -> str:
        try:
            expr = query.replace("$","")
            result = eval(expr, {"__builtins__": {}}, {})
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return str(result)
        except Exception as e:
            return f"Calculator Error: {e}"

class SearchTool:
    def run(self, query: str) -> str:
        try:
            wikipedia.set_lang("en")
            summary = wikipedia.summary(query, sentences=2, auto_suggest=True, redirect=True)
            return summary
        except Exception as e:
            return f"Wikipedia Error: {e}"

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
