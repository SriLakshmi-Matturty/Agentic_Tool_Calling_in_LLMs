# prompt_manager.py
class PromptManager:
    def build_tool_prompt(self, question: str) -> str:
        return f"""
You are a tool planner.
Choose tools from: "calculator" or "search".

Rules:
- For math, prices, or quantities → use calculator.
- Rewrite word problems into correct math expressions.
- For factual questions (people, history, science) → use search.
- Output JSON only, no text outside JSON.

Examples:

Q: What is 2+3?
A:
[{{"tool": "calculator", "query": "2+3"}}]

Q: Priyansh bought 3 chocolates for 15$, what is the cost for 25?
A:
[{{"tool": "calculator", "query": "25*(15/3)"}}]

Q: Who is the president of India?
A:
[{{"tool": "search", "query": "President of India"}}]

Now do the same:

Q: {question}
A:
"""

    def build_final_prompt(self, question: str, tool_results: list) -> str:
        return f"""
You are a helpful assistant.

User question: "{question}"

Tool results:
{tool_results}

Write the final answer clearly and concisely for the user.
Do NOT repeat instructions or JSON. Only output the answer.
"""
