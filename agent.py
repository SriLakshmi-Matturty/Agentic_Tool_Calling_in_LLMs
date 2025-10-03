# agent.py
import json
import re
from prompt_manager import PromptManager
from hf_llm import HFLLM

class Agent:
    def __init__(self, llm, prompt_manager, tools):
        self.llm = llm
        self.prompt_manager = prompt_manager
        self.tools = tools

    def run(self, question: str) -> str:
        # Step 1: Ask LLM for tool plan
        tool_prompt = self.prompt_manager.build_tool_prompt(question)
        raw_plan = self.llm.generate(tool_prompt)

        # Extract JSON safely
        match = re.search(r"\[[\s\S]*?\]", raw_plan)
        if not match:
            return f"Error: No valid JSON plan\nGot: {raw_plan}"
        try:
            plan = json.loads(match.group(0))
        except:
            return f"Error: Invalid JSON\nGot: {raw_plan}"

        # Step 2: Execute tools
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
        
        # If only one tool result and it's short, return it directly
        if len(results) == 1 and len(results[0]["result"]) < 100:
            return results[0]["result"]
        
        # Step 3: Ask LLM for final natural answer
        final_prompt = self.prompt_manager.build_tool_prompt(question, results)
        final_answer = self.llm.generate(final_prompt)
        return final_answer

