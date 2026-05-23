"""Base class shared by all DevMind agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from utils.llm_client import LLMClient


class BaseAgent(ABC):
    """Abstract base class that provides each agent an LLM client."""

    def __init__(self) -> None:
        self.llm = LLMClient()

    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the agent responsibility."""
