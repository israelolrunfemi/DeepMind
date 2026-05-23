"""In-memory event bus for broadcasting DevMind agent activity."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import AsyncGenerator


class EventType(str, Enum):
    """Event types emitted by agents, tools, and pipelines."""

    AGENT_START = "agent_start"
    AGENT_COMPLETE = "agent_complete"
    AGENT_ERROR = "agent_error"
    AGENT_RETRY = "agent_retry"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    PIPELINE_START = "pipeline_start"
    PIPELINE_COMPLETE = "pipeline_complete"


class EventBus:
    """Singleton-style event bus for SSE subscribers and recent history."""

    def __init__(self) -> None:
        self._subscribers: list[asyncio.Queue[dict]] = []
        self._history: list[dict] = []
        self._max_history = 100

    def emit(self, event_type: EventType, agent_name: str, data: dict | None = None) -> None:
        """Broadcast an event to current subscribers and keep bounded history."""

        event = {
            "type": event_type.value,
            "agent": agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data or {},
        }
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        for queue in list(self._subscribers):
            queue.put_nowait(event)

    async def subscribe(self) -> AsyncGenerator[str, None]:
        """Yield SSE-formatted event strings and unsubscribe on generator close."""

        queue: asyncio.Queue[dict] = asyncio.Queue()
        self._subscribers.append(queue)
        try:
            for event in self._history:
                yield f"data: {json.dumps(event)}\n\n"
            while True:
                event = await queue.get()
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            if queue in self._subscribers:
                self._subscribers.remove(queue)

    def get_history(self) -> list[dict]:
        """Return a copy of all events in history."""

        return list(self._history)


bus = EventBus()
