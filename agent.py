import json
from tools import CalculatorTool, SearchTool, KnowledgeBaseTool
from prompt_manager import PromptManager
from hf_llm import HFLLM

class Agent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt_manager = PromptManager()
        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool(),
            "knowledge_base": KnowledgeBaseTool(),
        }

    def answer(self, question: str):
        # Step 1: Get plan from LLM
        prompt = self.prompt_manager.build_prompt(question)
        raw_plan = self.llm.generate(prompt)

        # Step 1.5: Try to extract/repair JSON
        try:
            # Extract JSON-like part using regex
            match = re.search(r"\[.*\]", raw_plan, re.DOTALL)
            if match:
                raw_plan = match.group(0)
            plan = json.loads(raw_plan)
        except Exception as e:
            return f"Error parsing LLM output: {e}\nOutput was: {raw_plan}"

        # Step 2: Execute tool calls
        results = []
        for step in plan:
            tool_name = step.get("tool")
            query = step.get("query")
            tool = self.tools.get(tool_name)
            if tool:
                results.append(tool.run(query))
            else:
                results.append(f"Unknown tool: {tool_name}")

        # Step 3: Return final result
        return results[-1] if results else "No answer"


if __name__ == "__main__":
    llm = HFLLM("google/flan-t5-base")
    agent = Agent(llm)

    # Example GSM8K test
    q1 = "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?"
    print("Q:", q1)
    print("A:", agent.answer(q1))

    # Example WebQuestions test
    q2 = "Who is the president of France?"
    print("\nQ:", q2)
    print("A:", agent.answer(q2))
