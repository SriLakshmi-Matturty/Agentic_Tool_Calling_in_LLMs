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

Q: Julie is reading a 120-page book. Yesterday, she read 12 pages and today twice as many. If she wants to read half of the remaining pages tomorrow, how many pages should she read?
A: Today she read 12*2 = 24.
Total read so far: 12 + 24 = 36.
Remaining: 120 - 36 = 84.
Half of remaining: 84/2 = 42.
#### 42

Q: James writes a 3-page letter to 2 different friends twice a week. How many pages does he write a year?
A: He writes 3*2=6 pages per week for both friends.
He writes 6*2=12 pages weekly.
Then 12*52=624 pages yearly.
#### 624

Q: Mark planted 10 yellow flowers and 80% more purple ones. Green ones are 25% of yellow+purple. How many total flowers?
A: Purple = 10 * 1.8 = 18.
Yellow + purple = 28.
Green = 0.25 * 28 = 7.
Total = 28 + 7 = 35.
#### 35

Q: Albert buys 2 large pizzas (16 slices each) and 2 small pizzas (8 slices each). How many slices total?
A: Large: 2*16=32. Small: 2*8=16. Total: 32+16=48.
#### 48

Q: Ken's box weighs 2 lbs with jelly beans. Tripled with brownies, +2 lbs jelly beans, then doubled with gummy worms. Final weight?
A: Tripled: 2*3=6. Add 2: 6+2=8. Doubled: 8*2=16.
#### 16

Q: Alexis had $200, spent 30+46+38+11+18 on clothes, left with 16. How much were the shoes?
A: Total spent (excl. shoes): 143. Remaining budget = 200-16=184. Shoes = 184-143=41.
#### 41

Q: Tina earns $18/hr, 10h/day, 5 days, OT for >8h = 1.5x pay. How much total?
A: Regular: 8*18=144/day. OT: 2h/day * (18*1.5)=2*27=54/day. Weekly total=(144+54)*5=990.
#### 990
"""

        return examples.format(question)

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
        return examples.format(question)
