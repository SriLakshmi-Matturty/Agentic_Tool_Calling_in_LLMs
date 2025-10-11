import requests
from hf_llm import LocalLLM

class CalculatorTool:
    def execute(self, expr: str) -> str:
        try:
            # Safe eval for arithmetic expressions
            allowed_chars = "0123456789+-*/.() "
            if not all(c in allowed_chars for c in expr):
                return "Calculator Error: Invalid characters"
            result = eval(expr)
            return result
        except Exception as e:
            return f"Calculator Error: {e}"


class SearchTool:
    def __init__(self, serpapi_key=None, summarizer_model="mistralai/Mistral-7B-Instruct-v0.2"):
        self.serpapi_key = serpapi_key
        # Use the same model or a small one for summarization
        self.summarizer_llm = LocalLLM(model_name=summarizer_model)

    def execute(self, query: str) -> str:
        """Use SerpAPI to get a concise factual answer."""
        try:
            url = "https://serpapi.com/search"
            params = {"q": query, "api_key": self.serpapi_key}
            resp = requests.get(url, params=params)
            data = resp.json()

            # Collect snippets from search results
            snippets = []
            if "organic_results" in data:
                for r in data["organic_results"][:5]:
                    if "snippet" in r:
                        snippets.append(r["snippet"])
            text_block = " ".join(snippets)

            # Ask LLM to compress / extract concise factual entity names
            summarizer_prompt = f"""
Extract only the short factual answer(s) for the question below, in a concise comma-separated list.
Do not include explanations or long text.

Question: {query}
Context: {text_block}

Example output:
- If question: "What do Jamaican people speak?"
  Output: Jamaican Patois, English
"""
            short_answer = self.summarizer_llm.generate(summarizer_prompt, max_new_tokens=64).strip()
            return short_answer or text_block

        except Exception as e:
            return f"Search Error: {str(e)}"
