# prompt_manager.py
class PromptManager:
    def build_tool_prompt(self, question: str) -> str:
        return f"""
You are a tool planner.
Decide which tool to use: "calculator" or "search".

Rules:
- If the question is about math, prices, quantities, units → use "calculator".
- When using calculator, rewrite the question into a clean Python math expression.
  Example: "Priyansh bought 3 chocolates for 15$, cost for 25?" → "25*(15/3)"
- If the question is about facts, people, places, science, history → use "search".

Return ONLY valid JSON. Do not explain. Do not add extra text.

Example 1:
Question: What is 2+3?
Answer:
[{{"tool": "calculator", "query": "2+3"}}]

Example 2:
Question: Who is the president of India?
Answer:
[{{"tool": "search", "query": "President of India"}}]

Question: {question}
Answer:
"""

    def build_final_prompt(self, question: str, tool_results: list) -> str:
        return f"""
You are a helpful assistant.
The user asked: "{question}"

You have access to these tool results:
{tool_results}

Write a clear final answer for the user. Be concise and correct.
"""

