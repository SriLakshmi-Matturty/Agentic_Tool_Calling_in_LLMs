# Agentic_Tool_Calling_in_LLMs

A Python project that integrates a **Large Language Model (LLM)** with external tools like a **calculator** and **search engine** to answer both mathematical and factual questions intelligently. The agent classifies the question, decides the appropriate tool, and optionally summarizes results for factual queries.

---

## Features

- **Automatic Tool Selection:** Classifies questions as `math` or `factual` and routes them to the correct tool.
- **Calculator Integration:** Extracts Python expressions from natural language math questions and evaluates them safely.
- **Search Integration:** Fetches factual answers from the web via SerpAPI and summarizes results using the LLM.
- **Customizable LLM:** Supports any Hugging Face causal language model (Mistral, Qwen, TinyLlama, etc.).
- **Debug Friendly:** Prints step-by-step debug logs for classification, tool usage, and final answers.

---

## Folder Structure

```sh
├── agent.py # Main Agent class that handles question routing  
└── hf_llm.py # Local LLM wrapper using Hugging Face Transformers
└── prompt_manager.py # Prompts for final answer generation
└── tools.py # CalculatorTool and SearchTool implementations
└── requirements.txt # Python dependencies
└── .gitignore
└── Readme.md         
```

---
