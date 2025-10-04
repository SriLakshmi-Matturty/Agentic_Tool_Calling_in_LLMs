import requests

class CalculatorTool:
    def run(self, query: str) -> str:
        try:
            result = eval(query, {"__builtins__": {}}, {})
            return str(int(result) if isinstance(result, float) and result.is_integer() else result)
        except Exception as e:
            return f"Calculator Error: {e}"

class SearchTool:
    def run(self, query: str) -> str:
        try:
            # Try Wikipedia summary
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
            headers = {"User-Agent": "LLM-Agent/1.0"}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "extract" in data:
                    return data["extract"]

            # Fallback: Wikipedia search API
            search_url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "opensearch",
                "search": query,
                "limit": 1,
                "namespace": 0,
                "format": "json"
            }
            resp = requests.get(search_url, params=params, headers=headers, timeout=5)
            data = resp.json()
            if len(data) > 2 and data[2]:
                return data[2][0]
            return f"No info found for '{query}'"
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
