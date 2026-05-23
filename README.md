# DevMind 🧠
> An autonomous multi-agent AI system that takes a natural language task, plans it, writes Python code, executes it in a sandboxed environment, and self-heals from errors — all without human intervention.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-async-green)
![HuggingFace](https://img.shields.io/badge/Model-Qwen2.5--Coder-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## Architecture

```text
User task
  |
  v
FastAPI /run
  |
  v
PlannerAgent -> numbered execution plan
  |
  v
CoderAgent -> complete Python script
  |
  v
ExecutorAgent -> sandboxed subprocess result
  |
  v
Retry loop with error feedback, max 3 attempts
```

```text
devmind/
|-- main.py                  # FastAPI app entry point
|-- orchestrator.py          # Runs the full agent pipeline
|-- agents/
|   |-- __init__.py
|   |-- base_agent.py        # Base class all agents inherit from
|   |-- planner_agent.py     # Breaks task into a step-by-step plan
|   |-- coder_agent.py       # Writes Python code based on the plan
|   `-- executor_agent.py    # Runs code and returns result or error
|-- tools/
|   |-- __init__.py
|   |-- code_runner.py       # Executes Python code in a subprocess sandbox
|   |-- file_tools.py        # read_file, write_file
|   `-- package_installer.py # pip install missing packages
|-- config.py                # Config and constants
|-- schemas.py               # Pydantic models for requests/responses
|-- utils/
|   |-- __init__.py
|   |-- llm_client.py        # Async Hugging Face Inference API wrapper
|   `-- parser.py            # Parses LLM plans and code blocks
|-- .env.example
|-- requirements.txt
`-- README.md
```

## Tech Stack

| Layer | Tool |
| --- | --- |
| Runtime | Python 3.11+ |
| Backend | FastAPI |
| LLM | Hugging Face Inference API |
| Model | Qwen/Qwen2.5-Coder-7B-Instruct:nscale |
| Client | huggingface_hub.InferenceClient |
| HTTP client | httpx |
| Environment | python-dotenv |
| Terminal output | Rich |
| Execution | subprocess |
| Validation | Pydantic v2 |

## Setup

```powershell
git clone <repo-url>
cd devmind
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set:

```text
HF_TOKEN=your_token_here
```

Start the server:

```powershell
python -m uvicorn main:app --reload
```

## Endpoints

### GET /health

Response:

```json
{
  "status": "ok",
  "model": "Qwen/Qwen2.5-Coder-7B-Instruct:nscale"
}
```

### POST /run

Request:

```json
{
  "task": "Write a Python script that prints the first 10 Fibonacci numbers"
}
```

Response:

```json
{
  "success": true,
  "plan": ["Understand the Fibonacci sequence requirement.", "Write a loop that produces 10 values.", "Print the values."],
  "code": "a, b = 0, 1\nfor _ in range(10):\n    print(a)\n    a, b = b, a + b",
  "output": "0\n1\n1\n2\n3\n5\n8\n13\n21\n34\n",
  "error": null,
  "attempts": 1
}
```

## Agent Roles

PlannerAgent receives the raw user task, asks the LLM for a concise numbered plan, and returns parsed plan steps.

CoderAgent receives the plan and an optional previous execution error, asks the LLM for a complete Python script, and returns only the extracted code.

ExecutorAgent receives the code, runs it from an isolated temporary sandbox directory with a 15-second timeout, and returns a typed success or error result.
