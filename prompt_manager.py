# prompt_manager.py

class PromptManager:
    @staticmethod
    def build_final_prompt(question: str, tool_result_summary: str) -> str:
        """
        Builds a final LLM prompt to generate a factual, concise answer.
        
        Features:
        - Uses tool output if available.
        - Falls back on LLM knowledge when tool info is insufficient.
        - For 'Who is...' questions, prefers returning the person's name.
        """
        # Add detection for 'Who is' type questions
        lower_q = question.lower()
        if lower_q.startswith("who is") or lower_q.startswith("who's") or "prime minister" in lower_q or "president" in lower_q or "ceo" in lower_q:
            return (
                f"The user asked: {question}\n\n"
                f"Tool output:\n{tool_result_summary}\n\n"
                f"If the question refers to a specific person holding a role or title (like a Prime Minister, President, or CEO), "
                f"respond with the full name of that person as of now. "
                f"If the tool output is incomplete, use your own factual knowledge.\n\n"
                f"Give only the name and title in one clear sentence."
            )

        # Default path for other types of questions
        return (
            f"Use the information below if it is factual and relevant.\n"
            f"If the tool output is insufficient or missing, you may use your own knowledge.\n\n"
            f"Tool output:\n{tool_result_summary}\n\n"
            f"Question: {question}\n\n"
            f"Write a concise, factual answer in one or two sentences."
        )
