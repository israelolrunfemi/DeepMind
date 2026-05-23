"""Base class shared by all DevMind agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from utils.llm_client import LLMClient
from utils.event_bus import EventType, bus


class BaseAgent(ABC):
    """Abstract base class that provides each agent an LLM client."""

    def __init__(self) -> None:
        self.llm = LLMClient()

    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the agent responsibility."""

    def emit_start(self, data: dict | None = None) -> None:
        """Emit agent_start event with this class name."""

        bus.emit(EventType.AGENT_START, self.__class__.__name__, data or {})

    def emit_complete(self, data: dict | None = None) -> None:
        """Emit agent_complete event with this class name."""

        bus.emit(EventType.AGENT_COMPLETE, self.__class__.__name__, data or {})

    def emit_error(self, error: str) -> None:
        """Emit agent_error event with an error string."""

        bus.emit(EventType.AGENT_ERROR, self.__class__.__name__, {"error": error})

    def emit_retry(self, attempt: int, error: str) -> None:
        """Emit agent_retry event with attempt number and error."""

        bus.emit(EventType.AGENT_RETRY, self.__class__.__name__, {"attempt": attempt, "error": error})

    def emit_tool_call(self, tool_name: str, args: dict | None = None) -> None:
        """Emit tool_call event."""

        bus.emit(EventType.TOOL_CALL, self.__class__.__name__, {"tool": tool_name, "args": args or {}})

    def emit_tool_result(self, tool_name: str, result: dict | None = None) -> None:
        """Emit tool_result event."""

        bus.emit(EventType.TOOL_RESULT, self.__class__.__name__, {"tool": tool_name, "result": result or {}})
