# agent.py
from hf_llm import HFLLM
from tools import Calculator, DuckDuckGoSearch
from prompt_manager import PromptManager

class Agent:
    def __init__(self):
        self.llm = HFLLM()
        self.prompt_manager = PromptManager()
        self.tools = {
            "calculator": Calculator(),
            "search": DuckDuckGoSearch(),
        }

    def decide_tool(self, question):
        q = question.lower()
        if any(word in q for word in ["calculate", "evaluate", "+", "-", "*", "/", "sqrt", "power", "sum"]):
            return "calculator"
        return "search"

    def run(self, question):
        tool_name = self.decide_tool(question)
        print(f"\n🧩 Using tool: {tool_name}")
        tool_result = self.tools[tool_name].run(question)
        print(f"🔍 Tool result: {tool_result}\n")

        prompt = self.prompt_manager.build_prompt(question, tool_name, tool_result)
        response = self.llm.generate(prompt)
        print("🤖 Agent answer:", response)
        return response


if __name__ == "__main__":
    agent = Agent()
    while True:
        question = input("\nAsk a question (or type 'exit'): ")
        if question.lower() == "exit":
            break
        agent.run(question)
