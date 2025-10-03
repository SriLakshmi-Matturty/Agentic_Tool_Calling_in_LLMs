import re
import requests

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
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/140.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("extract", "No summary available.")
            else:
                return f"Wikipedia Error: HTTP {response.status_code}"
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
