"""Executor agent that runs generated code and returns its result."""

from __future__ import annotations

from agents.base_agent import BaseAgent
from config import EXECUTION_TIMEOUT
from schemas import ExecutionResult
from tools.code_runner import run_code


class ExecutorAgent(BaseAgent):
    """Run generated Python code inside the sandbox."""

    async def run(self, code: str) -> ExecutionResult:
        self.emit_start({"code_length": len(code)})
        result = await run_code(code, timeout=EXECUTION_TIMEOUT)
        if result.status == "error":
            self.emit_error(result.error or "Execution failed")
        else:
            self.emit_complete({"output_length": len(result.output or "")})
        return result
