import re
from tools import CalculatorTool, SearchTool
from prompt_manager import PromptManager
from hf_llm import LocalLLM

class Agent:
    def __init__(self, llm_model=None, serpapi_key=None):
        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool(serpapi_key)
        }
        self.llm = LocalLLM(model_name=llm_model)
        self.tool_calls = 0

    def decide_tool_and_expr(self, question: str):
       
        simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
        if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
            print(f"[DEBUG] Detected simple numeric expression: {question}")
            return "calculator", question

        prompt = f"""
Classify the question as 'math' or 'factual'.
If it is math, provide "math" and valid Python expression for the calculator, do not calculate answer just give the regular expression only
(Example: If the question is 
1) What is 2*3? then provide "math, 2*3"
2) Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May? then provide "math, 48+(48/2)"
3) Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?
   then provide "math, (12/60)*50"
4) Julie is reading a 120-page book. Yesterday, she was able to read 12 pages and today, she read twice as many pages as yesterday. If she wants to read half of the remaining pages tomorrow,
   how many pages should she read? then provide "math, 120-(12+(12*2))"
5) James writes a 3-page letter to 2 different friends twice a week.  How many pages does he write a year? then provide "math, ((3*2)*2)*52"
).
If it is factual then provide "factual, None".
(Example: If the question is
1) Who is President of America? then provide "factual, None"
2) What is the captial of Australia? then provide "factual, None"
3) What is the currency of India? then provide "factual, None"
4) What is an AI? then provide "factual, None"
5) Who is the synonym of happy? then provide "factual, None"
).
Do NOT generate extra questions or examples. Only give expression for the math question do not add extra questions to it.

Q: {question}
A:"""

        response = self.llm.generate(prompt, max_new_tokens=64).strip()
        print(f"[DEBUG] LLM response: {response}")

        if "math" in response.lower():
            expr_match = re.search(r"[\d\.\+\-\*/\(\)\s]+", response)
            if expr_match:
                expr = expr_match.group().strip()
                print(f"[DEBUG] Extracted expression: {expr}")
                return "calculator", expr

        print("[DEBUG] Using SearchTool for factual question.")
        return "search", None

    def run(self, question: str) -> str:
        """
        Main execution pipeline:
        1. Classify & extract expression
        2. Use appropriate tool
        3. Optionally summarize factual results via LLM
        """
        self.tool_calls = 0
        print(f"[INFO] Processing question: {question}")
        tool_name, expr = self.decide_tool_and_expr(question)

        if tool_name == "calculator":
            self.tool_calls += 1
            if expr:
                print(f"[DEBUG] Sending to CalculatorTool: {expr}")
                result = self.tools["calculator"].run(expr)
                return result
            return "Calculator Error: Unable to extract valid expression."

        if tool_name == "search":
            self.tool_calls += 1
            raw_context = self.tools["search"].run(question)
            print(f"[DEBUG] Raw SearchTool output: {raw_context}")

            # Build summarization prompt
            summary_prompt = PromptManager.build_final_prompt(
                question=question,
                tool_result_summary=raw_context
            )

            summarized = self.llm.generate(summary_prompt, max_new_tokens=128).strip()
            print(f"[DEBUG] Summarized answer: {summarized}")
            return summarized or raw_context

        return "Unable to handle question"
