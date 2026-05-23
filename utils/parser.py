"""Utilities for extracting plans and Python code from LLM output."""

from __future__ import annotations

import re
import json
from typing import Any


CODE_BLOCK_PATTERN = re.compile(r"```(?:python|py)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)
JSON_BLOCK_PATTERN = re.compile(r"```(?:json)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)
PLAN_STEP_PATTERN = re.compile(r"^\s*(?:\d+[\.)]|[-*])\s*(.+?)\s*$")


def extract_code_block(text: str) -> str:
    """Extract Python code from a fenced code block, or return stripped text."""

    match = CODE_BLOCK_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()


def extract_plan_steps(text: str) -> list[str]:
    """Parse numbered or bulleted plan steps into a list of strings."""

    steps: list[str] = []
    for line in text.splitlines():
        match = PLAN_STEP_PATTERN.match(line)
        if match:
            steps.append(match.group(1).strip())

    if steps:
        return steps

    fallback = [line.strip() for line in text.splitlines() if line.strip()]
    return fallback or [text.strip()]


def extract_json(text: str) -> dict[str, Any]:
    """Extract a JSON object from fenced or raw LLM output."""

    candidates = []
    block_match = JSON_BLOCK_PATTERN.search(text)
    if block_match:
        candidates.append(block_match.group(1).strip())
    candidates.append(text.strip())

    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        candidates.append(text[first_brace : last_brace + 1])

    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload

    raise ValueError("No valid JSON object found in LLM output")
