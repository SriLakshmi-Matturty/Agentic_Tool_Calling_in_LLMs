# agent.py
# agent.py
import re, json

class Agent:
    def __init__(self, llm, prompt_manager, tools):
        self.llm = llm
        self.prompt_manager = prompt_manager
        self.tools = tools

    def run(self, question: str) -> str:
        # Step 1: Tool Planning
        tool_prompt = self.prompt_manager.build_tool_prompt(question)
        raw_plan = self.llm.generate(tool_prompt)

        # Step 2: Extract JSON
        match = re.search(r"\[[\s\S]*?\]", raw_plan)
        if not match:
            return f"❌ Tool planner failed. Raw output:\n{raw_plan}"
        try:
            plan = json.loads(match.group(0))
        except Exception as e:
            return f"❌ Invalid JSON from LLM\n{raw_plan}\nError: {e}"

        # Step 3: Execute Tools
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

        # Step 4: Final Answer
        # 🚨 Keep the prompt minimal
        final_prompt = f"Q: {question}\nA: Based on the tool results {results}, the final answer is:"

        raw_answer = self.llm.generate(final_prompt).strip()

        # 🚨 Post-process to keep only clean answer (remove echoes of "Tool results", "You are", etc.)
        cleaned = re.sub(r"(?i)you are.*", "", raw_answer)  # drop repeated instructions
        cleaned = re.sub(r"(?i)tool results.*", "", cleaned)  # drop tool dump
        cleaned = cleaned.strip()

        return cleaned if cleaned else raw_answer

