# prompt_manager.py

class PromptManager:
    @staticmethod
    def build_prompt(query: str) -> str:
        return f"""You are a helpful AI agent with access to tools.

You can use:
1. Calculator – for math
2. Wikipedia – for factual or web-based questions

Decide which tool to use and respond concisely.

Question: {query}
"""
