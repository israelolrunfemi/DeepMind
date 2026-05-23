"""Persistent JSON session memory for DevMind."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from config import MEMORY_DIR


def _memory_path() -> Path:
    return Path(MEMORY_DIR)


def save_session(task: str, plan: list[str], code: str, output: str | None, success: bool, attempts: int) -> str:
    """Save a completed session to disk and return the session id."""

    session_id = str(uuid.uuid4())
    payload = {
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "task": task,
        "plan": plan,
        "code": code,
        "output": output,
        "success": success,
        "attempts": attempts,
    }
    memory_dir = _memory_path()
    memory_dir.mkdir(parents=True, exist_ok=True)
    (memory_dir / f"{session_id}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return session_id


def load_session(session_id: str) -> dict[str, Any] | None:
    """Load a specific session by id or return None when it does not exist."""

    path = _memory_path() / f"{session_id}.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def load_last_session() -> dict[str, Any] | None:
    """Load the most recent session by timestamp, or None if no sessions exist."""

    sessions = list_sessions()
    if not sessions:
        return None
    return load_session(str(sessions[0]["session_id"]))


def list_sessions() -> list[dict[str, Any]]:
    """Return session metadata sorted by timestamp descending."""

    memory_dir = _memory_path()
    if not memory_dir.exists():
        return []

    sessions: list[dict[str, Any]] = []
    for path in memory_dir.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        sessions.append(
            {
                "session_id": payload.get("session_id", path.stem),
                "timestamp": payload.get("timestamp", ""),
                "task": payload.get("task", ""),
                "success": bool(payload.get("success", False)),
                "attempts": int(payload.get("attempts", 0)),
            }
        )
    return sorted(sessions, key=lambda item: str(item["timestamp"]), reverse=True)


def delete_session(session_id: str) -> bool:
    """Delete a session file and return whether it existed."""

    path = _memory_path() / f"{session_id}.json"
    if not path.exists():
        return False
    try:
        path.unlink()
    except OSError:
        return False
    return True
