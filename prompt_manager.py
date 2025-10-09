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
        Few-shot examples for arithmetic reasoning (GSM8K-like).
        """
        examples = """
Q: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?
A: Natalia sold 48/2 = 24 clips in May.
Natalia sold 48+24 = 72 clips altogether in April and May.
#### 72

Q: Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?
A: Weng earns 12/60 = 0.2 per minute.
Working 50 minutes, she earned 0.2 * 50 = 10.
#### 10

Q: Betty is saving money for a new wallet which costs $100. Betty has only half of the money she needs. Her parents decided to give her $15 for that purpose, and her grandparents twice as much as her parents. How much more money does Betty need to buy the wallet?
A: In the beginning, Betty has only 100/2 = 50.
Betty's grandparents gave her 15*2 = 30.
This means, Betty needs 100 - 50 - 30 - 15 = 5 more.
#### 5
"""
        # Append the actual question at the end
        examples += f"\nQ: {question}\nA:"
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
        # Append the actual question
        examples += f"\nQ: {question}\nA:"
        return examples
