"""Endpoint smoke tests for DevMind upgrades."""

from __future__ import annotations

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_tools() -> None:
    response = client.get("/tools")
    assert response.status_code == 200
    assert "run_code" in response.json()["tools"]


def test_sessions() -> None:
    response = client.get("/sessions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_dashboard() -> None:
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_run_random_password() -> None:
    response = client.post("/run", json={"task": "write a python script that generates a random password"})
    assert response.status_code == 200
    payload = response.json()
    assert "success" in payload
    assert "code" in payload


def test_run_project_calculator() -> None:
    response = client.post("/run/project", json={"goal": "Build a simple Python CLI calculator"})
    assert response.status_code == 200
    payload = response.json()
    assert "success" in payload
    assert payload["project_name"]
