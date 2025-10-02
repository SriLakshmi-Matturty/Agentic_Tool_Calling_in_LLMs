# agent.py
import json
from prompt_manager import PromptManager
from tools import CalculatorTool, SearchTool, KnowledgeBaseTool
from hf_llm import HFLLM

class Agent:
    def __init__(self, llm, prompt_manager, tools):
        self.llm = llm
        self.prompt_manager = prompt_manager
        self.tools = tools

    def run(self, question: str) -> str:
    # Step 1: Prompt the LLM
    prompt = self.prompt_manager.build_prompt(question)
    raw_plan = self.llm.generate(prompt)

    try:
        plan = json.loads(raw_plan)
    except json.JSONDecodeError:
        # Retry with stricter instructions
        retry_prompt = self.prompt_manager.build_prompt(
            question + " (Respond ONLY with valid JSON!)"
        )
        raw_plan = self.llm.generate(retry_prompt)
        try:
            plan = json.loads(raw_plan)
        except json.JSONDecodeError:
            return f"Error: Invalid JSON from LLM\nGot: {raw_plan}"

    # Step 2: Execute the plan
    results = []
    for step in plan:
        tool_name = step.get("tool")
        query = step.get("query", "")
        tool = self.tools.get(tool_name)

        if tool:
            result = tool.run(query)
            results.append({"tool": tool_name, "query": query, "result": result})
        else:
            results.append({"tool": tool_name, "query": query, "result": "Unknown tool"})

    return results


if __name__ == "__main__":
    # Initialize everything
    pm = PromptManager()
    llm = HFLLM(model_name="EleutherAI/gpt-neo-125M", device=0)  # GPU recommended
    tools = {
        "calculator": CalculatorTool(),
        "search": SearchTool(),
        "knowledge_base": KnowledgeBaseTool(),
    }
    agent = Agent(llm, pm, tools)

    # User input loop
    while True:
        question = input("\nAsk me a question (or type 'exit'): ")
        if question.lower() == "exit":
            break

        output = agent.run(question)
        print("\n--- Results ---")
        for step in output:
            print(f"[{step['tool']}] {step['query']} -> {step['result']}")

