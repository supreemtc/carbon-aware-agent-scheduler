"""Tests for the FastAPI REST API in backend/main.py."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def valid_workflow_payload():
    return {
        "workflow_id": "wf-api-test-001",
        "tasks": [
            {
                "step_id": "step-1-preprocess",
                "task_type": "preprocessing",
                "description": "Preprocess dataset",
                "input_text": "Dataset input...",
                "estimated_tokens": 1000,
                "minimum_accuracy": 0.80,
                "deadline_seconds": 3,
                "delay_tolerance_seconds": 15,
                "priority": "normal",
            },
            {
                "step_id": "step-2-inference",
                "task_type": "inference",
                "description": "Execute agent inference",
                "input_text": "Inference prompt...",
                "estimated_tokens": 2000,
                "minimum_accuracy": 0.85,
                "deadline_seconds": 5,
                "delay_tolerance_seconds": 30,
                "priority": "high",
            },
        ],
        "latency_importance": 0.3,
        "cost_importance": 0.2,
        "carbon_importance": 0.4,
        "energy_importance": 0.1,
    }


def test_get_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_environment(client):
    response = client.get("/environment")
    assert response.status_code == 200
    data = response.json()
    assert "available_models" in data
    assert "available_regions" in data
    assert "execution_windows" in data
    assert len(data["available_models"]) == 3
    assert len(data["available_regions"]) == 4
    assert len(data["execution_windows"]) == 4


def test_post_plan_valid_workflow_returns_200(client, valid_workflow_payload):
    response = client.post("/plan", json=valid_workflow_payload)
    assert response.status_code == 200


def test_post_plan_preserves_workflow_id(client, valid_workflow_payload):
    response = client.post("/plan", json=valid_workflow_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == valid_workflow_payload["workflow_id"]


def test_post_plan_returns_2_scheduled_steps(client, valid_workflow_payload):
    response = client.post("/plan", json=valid_workflow_payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["scheduled_steps"]) == 2
    assert "total_estimated_cost" in data
    assert "total_estimated_energy_wh" in data
    assert "total_estimated_carbon_g" in data


def test_post_plan_infeasible_workflow_returns_400(client):
    infeasible_payload = {
        "workflow_id": "wf-api-infeasible",
        "tasks": [
            {
                "step_id": "step-impossible",
                "task_type": "deep_reasoning",
                "description": "Impossible task constraints",
                "input_text": "Sample text",
                "estimated_tokens": 1000,
                "minimum_accuracy": 0.999,
                "deadline_seconds": 1,
                "delay_tolerance_seconds": 0,
                "priority": "normal",
            }
        ],
        "latency_importance": 0.25,
        "cost_importance": 0.25,
        "carbon_importance": 0.25,
        "energy_importance": 0.25,
    }
    response = client.post("/plan", json=infeasible_payload)
    assert response.status_code == 400
    assert "No feasible execution plan exists" in response.json()["detail"]


def test_cors_behavior_localhost_3000(client):
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
