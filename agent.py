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
            return f"Tool planning failed. Raw output:\n{raw_plan}"
        
        try:
            plan = json.loads(match.group(0))
        except Exception as e:
            return f"Error: Invalid JSON\nGot: {raw_plan}\nError: {e}"

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

        # Step 3: If only one result (and simple), return directly
        if len(results) == 1 and isinstance(results[0]["result"], str) and len(results[0]["result"]) < 100:
            return results[0]["result"]

        # Step 4: Build final natural language answer
        final_prompt = self.prompt_manager.build_answer_prompt(question, results)
        final_answer = self.llm.generate(final_prompt)
        return final_answer.strip()

