# agent.py
from hf_llm import HuggingFaceLLM
from prompt_manager import PromptManager
from tools import CalculatorTool, WikipediaTool

class Agent:
    def __init__(self):
        self.llm = HuggingFaceLLM()
        self.tools = {
            "calculator": CalculatorTool(),
            "wikipedia": WikipediaTool()
        }

    def decide_tool(self, query: str) -> str:
        # Simple rule-based tool selection
        if any(op in query for op in ["+", "-", "*", "/", "sqrt", "power", "sin", "cos", "tan", "^"]):
            return "calculator"
        else:
            return "wikipedia"

    def run(self, query: str) -> str:
        tool_name = self.decide_tool(query)
        tool = self.tools[tool_name]
        print(f"\n🧩 Using tool: {tool_name}")

        result = tool.run(query)
        print(f"🔍 Tool result: {result}\n")

        prompt = PromptManager.build_prompt(f"Question: {query}\nTool result: {result}\nFinal Answer:")
        response = self.llm.generate(prompt)
        return response

if __name__ == "__main__":
    agent = Agent()
    while True:
        query = input("\nAsk me anything (or type 'exit'): ")
        if query.lower() == "exit":
            break
        print("\n🤖 Answer:")
        print(agent.run(query))
