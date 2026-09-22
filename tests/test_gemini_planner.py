"""Unit tests for the optional Gemini planner adapter.

These tests do not make real API calls.
"""

from types import SimpleNamespace

import pytest

from backend import gemini_planner


def _response(payload: dict):
    import json
    return SimpleNamespace(
        parsed=None,
        text=json.dumps(payload),
    )


def _valid_payload():
    return {
        "workflow_id": "test-workflow",
        "tasks": [
            {
                "step_id": "step-1",
                "task_type": "summarization",
                "description": "Summarize the input",
                "input_text": "Example input",
                "estimated_tokens": 1000,
                "minimum_accuracy": 0.9,
                "deadline_seconds": 5,
                "delay_tolerance_seconds": 0,
                "priority": "normal",
            }
        ],
        "latency_importance": 0.15,
        "cost_importance": 0.15,
        "carbon_importance": 0.40,
        "energy_importance": 0.20,
        "accuracy_importance": 0.10,
    }


def test_empty_request_rejected():
    with pytest.raises(ValueError, match="must not be empty"):
        gemini_planner.plan_from_text("")


def test_missing_api_key_rejected(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        gemini_planner.plan_from_text("Schedule a task")


def test_valid_response_is_pydantic_validated(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    class FakeModels:
        def generate_content(self, **kwargs):
            return _response(_valid_payload())

    class FakeClient:
        models = FakeModels()

    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(),
    )

    result = gemini_planner.plan_from_text("Schedule a summarization task")

    assert result.workflow_id == "test-workflow"
    assert result.tasks[0].minimum_accuracy == 0.9


def test_503_falls_back_to_next_model(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MAX_RETRIES", "0")

    calls = []

    class FakeModels:
        def generate_content(self, **kwargs):
            calls.append(kwargs["model"])
            if len(calls) == 1:
                raise RuntimeError("503 UNAVAILABLE")
            return _response(_valid_payload())

    class FakeClient:
        models = FakeModels()

    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(),
    )

    result = gemini_planner.plan_from_text("Schedule a task")

    assert result.workflow_id == "test-workflow"
    assert calls[0] == "gemini-3.8-flash"
    assert calls[1] == "gemini-3.7-flash"


def test_non_503_error_is_not_masked(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    class FakeModels:
        def generate_content(self, **kwargs):
            raise RuntimeError("401 INVALID_API_KEY")

    class FakeClient:
        models = FakeModels()

    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(),
    )

    with pytest.raises(RuntimeError, match="401"):
        gemini_planner.plan_from_text("Schedule a task")
