"""FastAPI entry point for the DevMind autonomous coding assistant."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse

from agents.project_agent import ProjectAgent
from config import (
    APP_NAME,
    APP_VERSION,
    DASHBOARD_ENDPOINT,
    DASHBOARD_TEMPLATE,
    EVENTS_ENDPOINT,
    HEALTH_ENDPOINT,
    HEALTH_STATUS,
    MODEL_NAME,
    PROJECT_RUN_ENDPOINT,
    RUN_ENDPOINT,
    SESSIONS_ENDPOINT,
    TOOLS_ENDPOINT,
)
from orchestrator import run
from schemas import HealthResponse, OrchestratorResult, ProjectRequest, ProjectResult, TaskRequest, ToolsResponse
from tools.memory import delete_session, list_sessions, load_session
from tools.registry import get_tool_descriptions
from utils.event_bus import bus
from utils.llm_client import LLMError


app = FastAPI(title=APP_NAME, version=APP_VERSION)


@app.post(RUN_ENDPOINT, response_model=OrchestratorResult)
async def run_task(request: TaskRequest) -> OrchestratorResult:
    """Plan, write, execute, and debug Python code for a user task."""

    try:
        return await run(request.task)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get(HEALTH_ENDPOINT, response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return service status and active model."""

    return HealthResponse(status=HEALTH_STATUS, model=MODEL_NAME)


@app.post(PROJECT_RUN_ENDPOINT, response_model=ProjectResult)
async def run_project(request: ProjectRequest) -> dict[str, Any]:
    """Build a multi-file project from a high-level goal."""

    try:
        return await ProjectAgent().run(request.goal)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get(SESSIONS_ENDPOINT)
async def sessions() -> list[dict[str, Any]]:
    """Return saved session metadata."""

    return list_sessions()


@app.get(f"{SESSIONS_ENDPOINT}/{{session_id}}")
async def session_detail(session_id: str) -> dict[str, Any]:
    """Return full saved session data."""

    session = load_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.delete(f"{SESSIONS_ENDPOINT}/{{session_id}}")
async def remove_session(session_id: str) -> dict[str, bool]:
    """Delete a saved session."""

    if not delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": True}


@app.get(TOOLS_ENDPOINT, response_model=ToolsResponse)
async def tools() -> ToolsResponse:
    """Return formatted descriptions of registered tools."""

    return ToolsResponse(tools=get_tool_descriptions())


@app.get(EVENTS_ENDPOINT)
async def events() -> StreamingResponse:
    """Stream agent and pipeline events as Server-Sent Events."""

    return StreamingResponse(
        bus.subscribe(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get(DASHBOARD_ENDPOINT, response_class=HTMLResponse)
async def dashboard() -> HTMLResponse:
    """Return the observability dashboard HTML."""

    try:
        html = Path(DASHBOARD_TEMPLATE).read_text(encoding="utf-8")
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Dashboard template not found: {exc}") from exc
    return HTMLResponse(html)
