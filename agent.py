# agent.py
class Agent:
    def __init__(self, llm, prompt_manager, tools):
        self.llm = llm
        self.prompt_manager = prompt_manager
        self.tools = tools

    def run(self, question: str) -> str:
        # Step 1: Tool Planning
        tool_prompt = self.prompt_manager.build_tool_prompt(question)
        raw_plan = self.llm.generate(tool_prompt)

        # Step 2: Parse JSON
        match = re.search(r"\[[\s\S]*?\]", raw_plan)
        if not match:
            return f"Error: No valid JSON plan\nGot: {raw_plan}"
        try:
            plan = json.loads(match.group(0))
        except Exception as e:
            return f"Error: Invalid JSON\nGot: {raw_plan}\nError: {e}"

        # Step 3: Execute tools
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

        # Step 4: Final natural answer
        final_prompt = self.prompt_manager.build_final_prompt(question, results)
        final_answer = self.llm.generate(final_prompt)
        return final_answer.strip()
