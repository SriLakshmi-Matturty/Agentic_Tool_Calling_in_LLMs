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
└── .gitignore # Git ignore file
└── Readme.md # Project description      
```

---

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd <your-repo-folder>
```
2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
---
## Usage
```python
from agent import Agent

# Initialize the agent
agent = Agent(
    llm_model="mistralai/Mistral-7B-Instruct-v0.2",  # or any other Hugging Face model
    serpapi_key="<YOUR_SERPAPI_KEY>",                # needed for factual search
    hf_token="<YOUR_HUGGINGFACE_TOKEN>"             # if required for private models
)

# Ask questions
print(agent.run("What is 2+3?"))
print(agent.run("Who is the President of the United States?"))

```
---
## Dependencies
```sh
Python 3.10+
torch
transformers
wikipedia
requests
sentencepiece
```
---
## Notes

- Ensure you have a SerpAPI key to use the SearchTool.
- LLM models can be GPU-intensive. Ensure CUDA is available for large models.
- CalculatorTool uses eval safely in a restricted environment for math expressions.
