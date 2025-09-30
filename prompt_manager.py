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
Return only valid JSON. No explanations.

Question: {question}
"""
