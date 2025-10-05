# tools.py
import math
import wikipedia

class CalculatorTool:
    name = "calculator"
    description = "Performs basic arithmetic and math operations."

    def run(self, query: str) -> str:
        try:
            result = eval(query, {"__builtins__": None}, math.__dict__)
            return str(result)
        except Exception as e:
            return f"Error: {e}"

class WikipediaTool:
    name = "wikipedia"
    description = "Fetches factual answers from Wikipedia."

    def run(self, query: str) -> str:
        try:
            wikipedia.set_lang("en")
            summary = wikipedia.summary(query, sentences=2)
            return summary
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple results found: {e.options[:5]}"
        except wikipedia.exceptions.PageError:
            return "No Wikipedia page found."
        except Exception as e:
            return f"Error: {e}"
