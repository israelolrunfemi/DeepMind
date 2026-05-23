"""Planner agent that turns a natural language task into ordered steps."""

from __future__ import annotations

from agents.base_agent import BaseAgent
from config import PLANNER_SYSTEM_PROMPT
from utils.parser import extract_plan_steps


class PlannerAgent(BaseAgent):
    """Create a concise execution plan for a coding task."""

    async def run(self, task: str) -> list[str]:
        response = await self.llm.complete(
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_prompt=task,
        )
        return extract_plan_steps(response)
