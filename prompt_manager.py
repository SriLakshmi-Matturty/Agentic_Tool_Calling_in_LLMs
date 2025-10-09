# prompt_manager.py

class PromptManager:
    @staticmethod
    def calculator_few_shot_prompt(question: str) -> str:
        """
        Few-shot examples for arithmetic reasoning.
        Solve step by step and return only the final numeric answer.
        """
        examples = """
Q: Natalia sold 48 clips in April, half as many in May. How many in total?
A: 48/2 = 24
48+24 = 72
#### 72

Q: Weng earns $12/hr and worked 50 minutes. How much did she earn?
A: 12/60*50 = 10
#### 10
"""
        examples += f"\nQ: {question}\nA: Solve step by step and provide only the numeric answer.\n####"
        return examples

    @staticmethod
    def search_few_shot_prompt(question: str) -> str:
        """
        Few-shot examples for factual lookup questions.
        """
        examples = """
Q: Who is the Prime Minister of India?
A: The Prime Minister of India is Narendra Modi.

Q: Who is the CEO of Tesla?
A: The CEO of Tesla is Elon Musk.
"""
        examples += f"\nQ: {question}\nA: Provide a concise factual answer in one sentence."
        return examples

