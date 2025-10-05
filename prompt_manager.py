# prompt_manager.py
class PromptManager:
    def build_prompt(self, question, tool_name=None, tool_result=None):
        system = (
            "You are a helpful AI agent with access to tools.\n"
            "You can use:\n"
            "1. Calculator – for math\n"
            "2. Search – for factual or web-based questions\n\n"
            "Decide which tool to use and give the final answer directly and concisely.\n\n"
        )

        if tool_name and tool_result:
            return (
                f"{system}Question: {question}\n"
                f"Tool used: {tool_name}\n"
                f"Tool result: {tool_result}\n\n"
                "Final concise answer:"
            )
        else:
            return f"{system}Question: {question}\nFinal concise answer:"
