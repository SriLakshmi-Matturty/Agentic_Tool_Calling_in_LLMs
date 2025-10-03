# prompt_manager.py

class PromptManager:
    def build_tool_prompt(self, question: str) -> str:
        """
        Step 1: Build a tool plan prompt.
        The LLM must output only JSON with the tools to use.
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

    def build_final_answer_prompt(self, question: str, tool_results: list) -> str:
        """
        Step 2: Build final answer prompt.
        The LLM must now use tool results to produce the final natural-language answer.
        """
        return f"""
You are an assistant that answers questions using tool results.

Question: {question}
Tool Results: {tool_results}

Answer:
"""

