"""Application configuration and constants for DevMind."""

from __future__ import annotations

import os

from dotenv import load_dotenv


load_dotenv()

APP_NAME = "DevMind"
APP_VERSION = "0.1.0"
HEALTH_ENDPOINT = "/health"
RUN_ENDPOINT = "/run"
HEALTH_STATUS = "ok"

HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HF_API_TOKEN")
MODEL_NAME = "Qwen/Qwen2.5-Coder-7B-Instruct:nscale"

MAX_RETRIES = 3
EXECUTION_TIMEOUT = 15
SANDBOX_DIR = os.getenv("DEVMIND_SANDBOX_DIR", "/tmp/devmind_sandbox")

LLM_MAX_TOKENS = 2048
LLM_TEMPERATURE = 0.2
HTTP_TIMEOUT = 60.0

PLANNER_SYSTEM_PROMPT = (
    "You are a senior software architect. Given a coding task, produce a clear, "
    "numbered step-by-step execution plan. Be concise. Output only the plan, no code."
)
CODER_SYSTEM_PROMPT = (
    "You are an expert Python developer. Write clean, complete, runnable Python code. "
    "Output ONLY a Python code block - no explanations, no markdown outside the code block."
)

DANGEROUS_MODULES = {
    "aiohttp",
    "ftplib",
    "httpx",
    "requests",
    "socket",
    "subprocess",
    "urllib",
}
DANGEROUS_BUILTINS = {"eval", "exec", "open", "__import__"}
