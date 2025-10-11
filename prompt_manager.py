class PromptManager:
    @staticmethod
    def build_final_prompt(question: str, tool_result_summary: str) -> str:
        """
        Formats the final prompt for LLM synthesis after tool calls.
        """
        return (
            f"Use ONLY the information below (do not invent facts).\n\n"
            f"Tool output:\n{tool_result_summary}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )
