# prompt_manager.py
class PromptManager:
    @staticmethod
    def build_final_prompt(question: str, tool_result_summary: str) -> str:
        """
        Minimal prompt for an LLM to synthesize a final answer when needed.
        """
        return (
            f"Use ONLY the information below (do not invent facts).\n\n"
            f"Tool output:\n{tool_result_summary}\n\n"
            f"Question: {question}\n\n"
            f"Write a concise factual answer (one or two sentences)."
        )
