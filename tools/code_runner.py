"""Subprocess-based Python code execution in an isolated sandbox directory."""

from __future__ import annotations

import ast
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from config import DANGEROUS_BUILTINS, DANGEROUS_MODULES, EXECUTION_TIMEOUT, SANDBOX_DIR
from schemas import ExecutionResult


def _validate_restricted_code(code: str) -> None:
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names]
            if isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
            for name in names:
                root_name = name.split(".", maxsplit=1)[0]
                if root_name in DANGEROUS_MODULES:
                    raise ValueError(f"Use of restricted module is not allowed: {root_name}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in DANGEROUS_BUILTINS:
                raise ValueError(f"Use of restricted builtin is not allowed: {node.func.id}")


def _sandbox_root() -> Path:
    if os.name == "nt" and SANDBOX_DIR.startswith("/tmp/"):
        return Path(tempfile.gettempdir()) / SANDBOX_DIR.removeprefix("/tmp/")
    return Path(SANDBOX_DIR)


async def run_code(code: str, timeout: int = EXECUTION_TIMEOUT) -> ExecutionResult:
    """Run Python code from a temporary file and return success output or an error."""

    try:
        _validate_restricted_code(code)
    except (SyntaxError, ValueError) as exc:
        return ExecutionResult(status="error", error=str(exc))

    sandbox_dir = _sandbox_root()
    try:
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        temp_dir = Path(tempfile.mkdtemp(prefix="run_", dir=sandbox_dir))
    except OSError as exc:
        return ExecutionResult(status="error", error=f"Could not create sandbox directory: {exc}")

    temp_file = temp_dir / "main.py"

    try:
        temp_file.write_text(code, encoding="utf-8")
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONIOENCODING": "utf-8",
            "PYTHONNOUSERSITE": "1",
        }
        completed = subprocess.run(
            [sys.executable, str(temp_file)],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return ExecutionResult(status="error", error=f"Execution timed out after {timeout} seconds: {exc}")
    except OSError as exc:
        return ExecutionResult(status="error", error=f"Execution failed: {exc}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    if completed.returncode == 0:
        return ExecutionResult(status="success", output=completed.stdout)

    error = completed.stderr or completed.stdout or f"Process exited with code {completed.returncode}"
    return ExecutionResult(status="error", error=error)
