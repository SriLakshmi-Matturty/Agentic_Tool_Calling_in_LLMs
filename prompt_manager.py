class PromptManager:
    @staticmethod
    def build_final_prompt(question: str, tool_result_summary: str) -> str:
        """
        Minimal prompt for LLM to synthesize a final answer from tool output.
        """
        return (
            f"Use ONLY the information below to answer the question.\n\n"
            f"Tool output:\n{tool_result_summary}\n\n"
            f"Question: {question}\n\n"
            f"Write a concise factual answer."
        )
