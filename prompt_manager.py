class PromptManager:
    def __init__(self):
        self.system_prompt = (
            "You are an AI reasoning agent. Your job is to break down a given "
            "question into tool calls. Available tools are: calculator, search, knowledge_base.\n\n"
            "Output must always be a list of JSON steps like:\n"
            "[{\"tool\": \"calculator\", \"query\": \"12/60\"}, {\"tool\": \"calculator\", \"query\": \"0.2*50\"}]"
        )

    def build_prompt(self, question: str) -> str:
        return f"{self.system_prompt}\n\nQuestion: {question}\nSteps:"
 
