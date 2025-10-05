# tools.py
import math
import requests

class Calculator:
    name = "calculator"
    description = "Performs basic arithmetic calculations."

    def run(self, query):
        try:
            result = eval(query, {"__builtins__": None}, math.__dict__)
            return str(result)
        except Exception:
            return "Error: Invalid mathematical expression."


class DuckDuckGoSearch:
    name = "search"
    description = "Performs a DuckDuckGo web search and returns a short factual answer."

    def run(self, query):
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
            response = requests.get(url, timeout=10).json()

            # Prefer AbstractText → RelatedTopics → fallback message
            if response.get("AbstractText"):
                return response["AbstractText"]
            elif response.get("RelatedTopics"):
                for topic in response["RelatedTopics"]:
                    if "Text" in topic:
                        return topic["Text"]
            return "No clear answer found online."
        except Exception as e:
            return f"Error fetching search results: {str(e)}"

