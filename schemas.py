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


class ProjectRequest(BaseModel):
    """Request body accepted by the /run/project endpoint."""

    goal: str = Field(min_length=1)


class ProjectResult(BaseModel):
    """Result returned by ProjectAgent."""

    success: bool
    project_name: str
    project_path: str
    files_created: list[str]
    dependencies_installed: list[str]
    run_output: str | None
    file_tree: dict
    error: str | None = None


class SessionMeta(BaseModel):
    """Session history metadata."""

    session_id: str
    timestamp: str
    task: str
    success: bool
    attempts: int


class SessionFull(SessionMeta):
    """Full saved session payload."""

    plan: list[str]
    code: str
    output: str | None


class ToolsResponse(BaseModel):
    """Available tool descriptions."""

    tools: str


class Event(BaseModel):
    """Observable agent or pipeline event."""

    type: str
    agent: str
    timestamp: str
    data: dict
