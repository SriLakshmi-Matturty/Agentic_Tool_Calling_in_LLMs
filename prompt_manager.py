# prompt_manager.py
class PromptManager:
    def build_tool_prompt(self, question: str) -> str:
        return f"""
You are a tool planner.
You must decide which tool to call.

Allowed tools:
- "calculator"
- "search"

Rules:
- If the question is about math, numbers, quantities, units → use "calculator".
- Rewrite into a valid Python math expression.
- If the question is about facts, people, places, science, history → use "search".

⚠️ IMPORTANT: Return ONLY valid JSON. Do NOT explain.

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
The user asked: "{question}"

Tool results: {tool_results}

Now, give the final short answer in plain language. 
Do not repeat the tool logs, just the answer.
"""

