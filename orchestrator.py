"""Orchestrates the DevMind plan, code, execute, and retry pipeline."""

from __future__ import annotations

from agents.coder_agent import CoderAgent
from agents.executor_agent import ExecutorAgent
from agents.planner_agent import PlannerAgent
from config import MAX_RETRIES
from schemas import OrchestratorResult
from tools.memory import save_session
from utils.event_bus import EventType, bus


async def run(task: str) -> OrchestratorResult:
    """Run the full autonomous DevMind pipeline for a coding task."""

    bus.emit(EventType.PIPELINE_START, "Orchestrator", {"task": task})
    planner = PlannerAgent()
    coder = CoderAgent()
    executor = ExecutorAgent()

    try:
        plan = await planner.run(task)
        error: str | None = None
        code = ""

        for attempt in range(MAX_RETRIES):
            code = await coder.run(plan, error=error, attempt=attempt + 1)
            result = await executor.run(code)

            if result.status == "success":
                response = OrchestratorResult(
                    plan=plan,
                    code=code,
                    output=result.output,
                    attempts=attempt + 1,
                    success=True,
                )
                save_session(task, plan, code, result.output, True, attempt + 1)
                bus.emit(EventType.PIPELINE_COMPLETE, "Orchestrator", {"success": True, "attempts": attempt + 1})
                return response

            error = result.error
            if error:
                bus.emit(EventType.AGENT_RETRY, "Orchestrator", {"attempt": attempt + 1, "error": error})

        response = OrchestratorResult(
            plan=plan,
            code=code,
            output=None,
            error=error,
            attempts=MAX_RETRIES,
            success=False,
        )
        save_session(task, plan, code, None, False, MAX_RETRIES)
        bus.emit(EventType.PIPELINE_COMPLETE, "Orchestrator", {"success": False, "attempts": MAX_RETRIES})
        return response
    except (RuntimeError, ValueError, TypeError) as exc:
        bus.emit(EventType.PIPELINE_COMPLETE, "Orchestrator", {"success": False, "error": str(exc)})
        raise
