def decide_tool_and_expr(self, question: str):
    """
    Decide which tool to call based on the question.
    Returns: (tool_name, expression_or_query)
    """
    # Step 0: detect simple numeric expressions
    simple_math_pattern = r"^[\d\s\.\+\-\*/\(\)]+$"
    if re.fullmatch(simple_math_pattern, question.replace(" ", "")):
        print(f"[DEBUG] Simple numeric expression detected: {question}")
        return "calculator", question

    # Step 1: classify question using classifier LLM (STRICT prompt)
    classifier_prompt = (
        f"You are a classifier. Reply with exactly one word: 'math' or 'factual'.\n\n"
        f"Examples:\n"
        f"Q: Who is the president of America?\nA: factual\n"
        f"Q: What is 17*24?\nA: math\n"
        f"Q: What is AI?\nA: factual\n"
        f"Q: Julie read 12 pages yesterday, today twice as many. "
        f"If she reads half remaining tomorrow, how many pages should she read?\nA: math\n\n"
        f"Question: {question}\nAnswer:"
    )

    classification = self.classifier_llm.generate(
        classifier_prompt, max_new_tokens=4
    ).strip().lower()
    print(f"[DEBUG] Raw classifier output: {classification}")

    # Step 1.1: Post-process to ensure valid one-word output
    if "math" in classification:
        classification = "math"
    elif "factual" in classification:
        classification = "factual"
    else:
        # Default fallback
        classification = "factual"
    print(f"[DEBUG] Final classification: {classification}")

    # Step 2: if math, send to math LLM to extract symbolic expression
    if classification == "math":
        math_prompt = f"""
You are a math expression extractor.

Instructions:
1. Respond ONLY with a JSON object containing a symbolic expression.
2. The JSON must have ONLY one key: "expression".
   Example: {{"expression": "2+3"}}
3. DO NOT compute the answer.
4. DO NOT include explanations, reasoning, code, "result", or "=".
5. Use only +, -, *, /, parentheses, pi, numbers, and variables.

Question: {question}
"""
        response = self.math_llm.generate(math_prompt, max_new_tokens=128).strip()
        print(f"[DEBUG] Math LLM raw response: {response}")

        # Try extracting JSON first
        parsed = self.extract_json_from_text(response)
        if parsed and "expression" in parsed:
            expr = self.clean_expression(parsed["expression"])
            print(f"[DEBUG] Using CalculatorTool from JSON expression: {expr}")
            return "calculator", expr
        else:
            # JSON not found, fallback to regex
            print("[DEBUG] Could not extract JSON, trying regex fallback")
            expr = self.extract_expression_from_text(response)
            if expr:
                expr = self.clean_expression(expr)
                print(f"[DEBUG] Using CalculatorTool from regex extracted expression: {expr}")
                return "calculator", expr

        # If all fails
        print("[DEBUG] Could not extract expression, defaulting to SearchTool")
        return "search", question

    else:
        # Factual question → use SearchTool
        print("[DEBUG] Using SearchTool for factual question.")
        return "search", question
