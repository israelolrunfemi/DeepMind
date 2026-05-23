"""Orchestrates the DevMind plan, code, execute, and retry pipeline."""

from __future__ import annotations

from agents.coder_agent import CoderAgent
from agents.executor_agent import ExecutorAgent
from agents.planner_agent import PlannerAgent
from config import MAX_RETRIES
from schemas import OrchestratorResult


async def run(task: str) -> OrchestratorResult:
    """Run the full autonomous DevMind pipeline for a coding task."""

    planner = PlannerAgent()
    coder = CoderAgent()
    executor = ExecutorAgent()

    plan = await planner.run(task)
    error: str | None = None
    code = ""

    for attempt in range(MAX_RETRIES):
        code = await coder.run(plan, error=error)
        result = await executor.run(code)

        if result.status == "success":
            return OrchestratorResult(
                plan=plan,
                code=code,
                output=result.output,
                attempts=attempt + 1,
                success=True,
            )

        error = result.error

    return OrchestratorResult(
        plan=plan,
        code=code,
        output=None,
        error=error,
        attempts=MAX_RETRIES,
        success=False,
    )
