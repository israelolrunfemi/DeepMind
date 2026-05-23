"""Utilities for extracting plans and Python code from LLM output."""

from __future__ import annotations

import re


CODE_BLOCK_PATTERN = re.compile(r"```(?:python|py)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)
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
