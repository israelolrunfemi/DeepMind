"""Planner agent that turns a natural language task into ordered steps."""

from __future__ import annotations

from agents.base_agent import BaseAgent
from config import PLANNER_SYSTEM_PROMPT
from utils.parser import extract_plan_steps


class PlannerAgent(BaseAgent):
    """Create a concise execution plan for a coding task."""

    async def run(self, task: str) -> list[str]:
        self.emit_start({"task": task})
        try:
            response = await self.llm.complete(
                system_prompt=PLANNER_SYSTEM_PROMPT,
                user_prompt=task,
            )
            plan = extract_plan_steps(response)
        except (RuntimeError, ValueError) as exc:
            self.emit_error(str(exc))
            raise
        self.emit_complete({"steps": len(plan)})
        return plan
