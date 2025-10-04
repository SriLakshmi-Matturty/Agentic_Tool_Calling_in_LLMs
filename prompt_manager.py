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

Return ONLY valid JSON.

Example 1:
Question: What is 2+3?
Answer:
[
  {{"tool": "calculator", "query": "2+3"}}
]

Example 2:
Question: Priyansh bought 3 chocolates for 15$, then what is the cost for 25 chocolates?
Answer:
[
  {{"tool": "calculator", "query": "25*(15/3)"}}
]

Example 3:
Question: Who is the president of India?
Answer:
[
  {{"tool": "search", "query": "President of India"}}
]

Question: {question}
Answer:
"""

    def build_answer_prompt(self, question: str, tool_results: list) -> str:
        return f"""
You are a helpful assistant. A user asked: "{question}"

You had access to tools. Here are their results:
{tool_results}

Now, write the FINAL answer in natural language.
Keep it short and direct.
"""

