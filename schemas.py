"""Pydantic models for DevMind request, response, and agent data shapes."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TaskRequest(BaseModel):
    """Request body accepted by the /run endpoint."""

    task: str = Field(min_length=1)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model: str


class ExecutionResult(BaseModel):
    """Result produced by the executor tool and agent."""

    status: str = Field(pattern="^(success|error)$")
    output: str | None = None
    error: str | None = None


class OrchestratorResult(BaseModel):
    """Full response returned after planning, coding, executing, and retrying."""

    success: bool
    plan: list[str]
    code: str
    output: str | None = None
    error: str | None = None
    attempts: int
