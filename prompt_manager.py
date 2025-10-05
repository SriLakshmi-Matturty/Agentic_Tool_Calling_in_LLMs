# prompt_manager.py
class PromptManager:
    @staticmethod
    def build_prompt(question: str, tool_result: str) -> str:
        return f"""You are a helpful AI agent that answers user questions using tools.

Tool Outputs:
{tool_result}

Now based on the above tool result, provide a **final concise and factual answer** to the following question.

Question: {question}

Answer only with the final factual response. Do not repeat the question or mention tools.
"""
