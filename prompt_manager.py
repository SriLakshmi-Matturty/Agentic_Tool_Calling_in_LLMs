# prompt_manager.py

class PromptManager:
    @staticmethod
    def build_final_prompt(question: str, tool_result_summary: str) -> str:
        """
        Minimal prompt for an LLM to synthesize a final answer when needed.
        """
        return (
            f"Use ONLY the information below (do not invent facts).\n\n"
            f"Tool output:\n{tool_result_summary}\n\n"
            f"Question: {question}\n\n"
            f"Write a concise factual answer (one or two sentences)."
        )

    @staticmethod
    def calculator_few_shot_prompt(question: str) -> str:
        """
        Few-shot examples for arithmetic reasoning (GSM8K-like), with clear instructions.
        """
        examples = """
Solve the following problems step by step, showing calculations, and return only the final numeric answer.

Q: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
A: Natalia sold 48/2 = 24 clips in May.
Natalia sold 48+24 = 72 clips altogether in April and May.
#### 72

Q: Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?
A: Weng earns 12/60 = 0.2 per minute.
Working 50 minutes, she earned 0.2 * 50 = 10.
#### 10
"""
        # Append the current question explicitly
        examples += f"\nQ: {question}\nA: Solve this question step by step, then give only the final numeric answer.\n####"
        return examples

    @staticmethod
    def search_few_shot_prompt(question: str) -> str:
        """
        Few-shot examples for factual lookup questions.
        """
        examples = """
Q: Who is the president of India?
A: The current president of India is Droupadi Murmu.

Q: Who is the CEO of Tesla?
A: The CEO of Tesla is Elon Musk.

Q: Who is the Prime Minister of India?
A: The Prime Minister of India is Narendra Modi.
"""
        examples += f"\nQ: {question}\nA: Provide a concise, factual answer in one sentence."
        return examples
