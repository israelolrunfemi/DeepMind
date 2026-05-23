"""Central registry of tools available to DevMind agents."""

from __future__ import annotations

import inspect
from typing import Any, Callable

from pydantic import BaseModel

from tools.code_runner import run_code
from tools.file_tools import (
    create_directory,
    delete_file,
    get_file_tree,
    list_directory,
    move_file,
    read_file,
    write_file,
)
from tools.memory import list_sessions, load_last_session, save_session
from tools.package_installer import install_package
from tools.web_search import search as web_search


TOOLS: dict[str, Callable[..., Any]] = {
    "run_code": run_code,
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "delete_file": delete_file,
    "create_directory": create_directory,
    "move_file": move_file,
    "get_file_tree": get_file_tree,
    "install_package": install_package,
    "web_search": web_search,
    "load_last_session": load_last_session,
    "list_sessions": list_sessions,
}


def _normalize_result(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        return result
    if isinstance(result, BaseModel):
        return result.model_dump()
    if result is True:
        return {"status": "success"}
    if result is False:
        return {"status": "error", "error": "Tool returned false"}
    if isinstance(result, str):
        return {"status": "success", "result": result}
    if isinstance(result, list):
        return {"status": "success", "result": result}
    return {"status": "success", "result": result}


async def call_tool(name: str, **kwargs: Any) -> dict[str, Any]:
    """Call a registered tool by name with keyword arguments."""

    tool = TOOLS.get(name)
    if tool is None:
        return {"status": "error", "error": "Tool not found"}
    try:
        result = tool(**kwargs)
        if inspect.isawaitable(result):
            result = await result
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        return {"status": "error", "error": str(exc)}
    return _normalize_result(result)


def get_tool_names() -> list[str]:
    """Return all registered tool names."""

    return sorted(TOOLS)


def get_tool_descriptions() -> str:
    """Return formatted tool names and docstrings for prompt injection."""

    descriptions = []
    for name in get_tool_names():
        doc = inspect.getdoc(TOOLS[name]) or "No description available."
        descriptions.append(f"- {name}: {doc.splitlines()[0]}")
    return "\n".join(descriptions)
