class PromptManager:
    @staticmethod
    def build_final_prompt(question: str, tool_result_summary: str) -> str:
        """
        Minimal prompt for LLM to synthesize a final answer from tool output.
        """
        return (
            f"Use ONLY the information below to answer the question.\n\n"
            f"Tool output:\n{tool_result_summary}\n\n"
            f"Question: {question}\n\n"
            f"Write a concise factual answer."
        )

    @staticmethod
    def classify_question_prompt(question: str) -> str:
        """
        Few-shot classification for type of question: factual or math.
        """
        examples = """
Q: Who is the president of India?
A: factual

Q: What is 235 * 47?
A: math

Q: Priyansh bought 3 chocolates for $15. Cost for 25?
A: math

Q: What is the capital city of Australia?
A: factual
"""
        return examples + f"\nQ: {question}\nA:"

    @staticmethod
    def calculator_few_shot_prompt(question: str) -> str:
        """
        Few-shot examples for arithmetic reasoning.
        """
        examples = """
Q: Natalia sold 48 clips to her friends and half as many more. Total clips?
A: 48/2=24; 48+24=72
#### 72

Q: Weng earns $12/hr, works 50 mins. Earnings?
A: 12/60*50=10
#### 10

Q: Priyansh bought 3 chocolates for $15. Cost for 25?
A: 15/3*25=125
#### 125
"""
        return examples + f"\nQ: {question}\nA:"
