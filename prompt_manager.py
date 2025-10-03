# prompt_manager.py

class PromptManager:
    def build_prompt(self, question: str) -> str:
        """
        Build a structured prompt for the LLM.
        LLM must output only JSON in the format:
        [
          {"tool": "calculator", "query": "expression"},
          {"tool": "search", "query": "search query"},
          {"tool": "knowledge_base", "query": "fact"}
        ]
        """
        return f"""
You are a tool-calling planner.
You must return ONLY valid JSON, nothing else.

Example 1:
Question: What is 2+3?
Answer:
[
  {{"tool": "calculator", "query": "2+3"}}
]

Example 2:
Question: Who is the Prime Minister of India?
Answer:
[
  {{"tool": "search", "query": "Prime Minister of India"}}
]

Question: {question}
Answer:
"""


