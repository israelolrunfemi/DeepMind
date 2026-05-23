"""FastAPI entry point for the DevMind autonomous coding assistant."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from config import APP_NAME, APP_VERSION, HEALTH_ENDPOINT, HEALTH_STATUS, MODEL_NAME, RUN_ENDPOINT
from orchestrator import run
from schemas import HealthResponse, OrchestratorResult, TaskRequest
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
