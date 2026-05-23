"""Coder agent that asks the LLM for a complete Python script."""

from __future__ import annotations

from agents.base_agent import BaseAgent
from config import CODER_SYSTEM_PROMPT
from utils.parser import extract_code_block


class CoderAgent(BaseAgent):
    """Generate runnable Python code from a plan and optional previous error."""

    async def run(self, plan: list[str], error: str | None = None) -> str:
        numbered_plan = "\n".join(f"{index}. {step}" for index, step in enumerate(plan, start=1))
        user_prompt = f"Execution plan:\n{numbered_plan}\n\nWrite the complete Python script."
        if error:
            user_prompt = (
                f"{user_prompt}\n\nThe previous attempt failed with this error:\n{error}\n\n"
                "Fix the bug and return the full corrected script."
            )

        response = await self.llm.complete(
            system_prompt=CODER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        return extract_code_block(response)
