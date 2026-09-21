"""Integration tests verifying Person 2 multi-objective scoring, constraints, and baseline comparisons."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models import (
    ExecutionPlan,
    ExecutionWindow,
    ModelProfile,
    RegionProfile,
    WorkflowRequest,
    WorkflowTask,
)
from backend.optimizer import optimize_task, select_baseline_candidate
from backend.scheduler import compare_workflow, load_scheduler_data, schedule_workflow


@pytest.fixture
def client():
    return TestClient(app)


# TEST 1: A workflow with multiple feasible candidates.
# Verify:
# - selected accuracy >= minimum_accuracy
# - selected latency <= deadline
# - selected model exists
# - selected region exists
# - score is returned
def test_workflow_with_multiple_feasible_candidates():
    models, regions, windows = load_scheduler_data()
    model_ids = {m.model_id for m in models}
    region_ids = {r.region_id for r in regions}

    task = WorkflowTask(
        step_id="step-multi-candidates",
        task_type="analysis",
        description="Standard task with wide bounds",
        input_text="Data input...",
        estimated_tokens=1500,
        minimum_accuracy=0.70,  # All models qualify (0.78, 0.85, 0.92)
        deadline_seconds=5,  # 5000ms: all regions qualify
        delay_tolerance_seconds=30,
        priority="normal",
    )
    workflow = WorkflowRequest(
        workflow_id="wf-test-1",
        tasks=[task],
        accuracy_importance=0.30,
        latency_importance=0.20,
        cost_importance=0.20,
        carbon_importance=0.15,
        energy_importance=0.15,
    )
    plan = schedule_workflow(workflow)
    assert isinstance(plan, ExecutionPlan)
    assert len(plan.scheduled_steps) == 1

    step = plan.scheduled_steps[0]
    assert step.estimated_accuracy >= task.minimum_accuracy
    assert step.estimated_latency_ms <= task.deadline_seconds * 1000
    assert step.selected_model in model_ids
    assert step.selected_region in region_ids
    assert isinstance(step.score, float)
    assert 0.0 <= step.score <= 1.0


# TEST 2: A workflow where every candidate violates the accuracy or latency constraint.
# Verify:
# - no feasible plan is returned
# - existing error handling works
def test_workflow_all_candidates_violate_constraints():
    # 2a. Accuracy constraint violation
    task_acc_fail = WorkflowTask(
        step_id="step-acc-fail",
        task_type="hard_task",
        description="Impossible accuracy",
        input_text="input",
        estimated_tokens=500,
        minimum_accuracy=0.999,  # No model exceeds 0.92
        deadline_seconds=10,
        delay_tolerance_seconds=0,
        priority="high",
    )
    wf_acc = WorkflowRequest(workflow_id="wf-fail-acc", tasks=[task_acc_fail])
    with pytest.raises(ValueError, match="No feasible execution plan exists"):
        schedule_workflow(wf_acc)

    # 2b. Latency constraint violation
    task_lat_fail = WorkflowTask(
        step_id="step-lat-fail",
        task_type="fast_task",
        description="Impossible deadline",
        input_text="input",
        estimated_tokens=500,
        minimum_accuracy=0.70,
        deadline_seconds=1,  # 1000ms
        delay_tolerance_seconds=0,
        priority="high",
    )
    models = [
        ModelProfile(
            model_id="slow-model",
            model_name="Slow Model",
            accuracy_score=0.90,
            average_latency_ms=2000.0,
            cost_per_1k_tokens=0.001,
            energy_wh_per_1k_tokens=0.1,
            context_window=1000,
        )
    ]
    regions = [
        RegionProfile(
            region_id="r1",
            region_name="Region 1",
            base_latency_ms=100.0,
            carbon_intensity_gco2_kwh=100.0,
        )
    ]
    windows = [
        ExecutionWindow(
            window_id="w1",
            scheduled_offset_seconds=0,
            carbon_multiplier=1.0,
        )
    ]
    with pytest.raises(ValueError, match="No feasible execution plan exists"):
        optimize_task(task_lat_fail, models, regions, windows)


# TEST 3: Verify lower carbon/energy/cost candidates affect the score when accuracy and latency remain feasible.
def test_lower_carbon_cost_energy_affect_score():
    models = [
        ModelProfile(
            model_id="m1",
            model_name="Model 1",
            accuracy_score=0.85,
            average_latency_ms=200.0,
            cost_per_1k_tokens=0.001,
            energy_wh_per_1k_tokens=0.05,
            context_window=10000,
        )
    ]
    regions = [
        RegionProfile(
            region_id="dirty-grid",
            region_name="Dirty Grid",
            base_latency_ms=50.0,
            carbon_intensity_gco2_kwh=600.0,
        ),
        RegionProfile(
            region_id="clean-grid",
            region_name="Clean Grid",
            base_latency_ms=50.0,
            carbon_intensity_gco2_kwh=30.0,
        ),
    ]
    windows = [
        ExecutionWindow(window_id="w0", scheduled_offset_seconds=0, carbon_multiplier=1.0),
    ]
    task = WorkflowTask(
        step_id="step-carbon-impact",
        task_type="inference",
        description="Check carbon impact on score",
        input_text="Sample input",
        estimated_tokens=1000,
        minimum_accuracy=0.80,
        deadline_seconds=2,
        delay_tolerance_seconds=0,
        priority="normal",
    )
    # With carbon_importance > 0, clean grid should be chosen
    step = optimize_task(
        task=task,
        models=models,
        regions=regions,
        windows=windows,
        accuracy_importance=0.2,
        latency_importance=0.2,
        cost_importance=0.2,
        energy_importance=0.1,
        carbon_importance=0.3,
    )
    assert step.selected_region == "clean-grid"
    assert step.score > 0.0


# TEST 4: Verify higher accuracy contributes positively to the score.
def test_higher_accuracy_contributes_positively():
    models = [
        ModelProfile(
            model_id="low-acc",
            model_name="Lower Accuracy Model",
            accuracy_score=0.80,
            average_latency_ms=200.0,
            cost_per_1k_tokens=0.001,
            energy_wh_per_1k_tokens=0.05,
            context_window=10000,
        ),
        ModelProfile(
            model_id="high-acc",
            model_name="Higher Accuracy Model",
            accuracy_score=0.95,
            average_latency_ms=200.0,
            cost_per_1k_tokens=0.001,
            energy_wh_per_1k_tokens=0.05,
            context_window=10000,
        ),
    ]
    regions = [
        RegionProfile(
            region_id="r1",
            region_name="Region 1",
            base_latency_ms=50.0,
            carbon_intensity_gco2_kwh=100.0,
        )
    ]
    windows = [
        ExecutionWindow(window_id="w0", scheduled_offset_seconds=0, carbon_multiplier=1.0)
    ]
    task = WorkflowTask(
        step_id="step-acc-test",
        task_type="test",
        description="Check accuracy contribution",
        input_text="test",
        estimated_tokens=1000,
        minimum_accuracy=0.75,
        deadline_seconds=2,
        delay_tolerance_seconds=0,
        priority="normal",
    )
    step = optimize_task(
        task=task,
        models=models,
        regions=regions,
        windows=windows,
        accuracy_importance=0.50,
        latency_importance=0.10,
        cost_importance=0.10,
        carbon_importance=0.15,
        energy_importance=0.15,
    )
    assert step.selected_model == "high-acc"
    assert step.estimated_accuracy == 0.95


# TEST 5: Verify existing API endpoint /plan still works.
def test_api_plan_endpoint_works(client):
    payload = {
        "workflow_id": "wf-api-int-001",
        "tasks": [
            {
                "step_id": "step-1",
                "task_type": "summarization",
                "description": "Summarize",
                "input_text": "Sample text...",
                "estimated_tokens": 1000,
                "minimum_accuracy": 0.80,
                "deadline_seconds": 4,
                "delay_tolerance_seconds": 15,
                "priority": "normal",
            }
        ],
        "accuracy_importance": 0.30,
        "latency_importance": 0.20,
        "cost_importance": 0.20,
        "carbon_importance": 0.15,
        "energy_importance": 0.15,
    }
    response = client.post("/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == "wf-api-int-001"
    assert len(data["scheduled_steps"]) == 1
    assert data["scheduled_steps"][0]["score"] > 0.0


# TEST 6: Verify existing /health still works.
def test_api_health_endpoint_works(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# Baseline comparison verification
def test_baseline_selection_and_comparison(client):
    models, regions, windows = load_scheduler_data()
    task = WorkflowTask(
        step_id="step-base",
        task_type="reasoning",
        description="Check baseline selection",
        input_text="Sample input",
        estimated_tokens=2000,
        minimum_accuracy=0.75,
        deadline_seconds=5,
        delay_tolerance_seconds=30,
        priority="high",
    )
    # Baseline must select the highest accuracy feasible candidate (gemini-1.5-pro has 0.92)
    baseline_step = select_baseline_candidate(task, models, regions, windows)
    assert baseline_step.selected_model == "gemini-1.5-pro"
    assert baseline_step.estimated_accuracy == 0.92

    # Compare workflow
    wf = WorkflowRequest(workflow_id="wf-comp-001", tasks=[task])
    comparison = compare_workflow(wf)
    assert "optimized_plan" in comparison
    assert "baseline_plan" in comparison
    assert "comparison" in comparison
    assert "carbon_savings_pct" in comparison["comparison"]

    # Test POST /compare endpoint
    payload = {
        "workflow_id": "wf-compare-api",
        "tasks": [
            {
                "step_id": "step-1",
                "task_type": "summarization",
                "description": "Summarize",
                "input_text": "Sample text...",
                "estimated_tokens": 1000,
                "minimum_accuracy": 0.80,
                "deadline_seconds": 4,
                "delay_tolerance_seconds": 15,
                "priority": "normal",
            }
        ],
    }
    res = client.post("/compare", json=payload)
    assert res.status_code == 200
    comp_data = res.json()
    assert "optimized_plan" in comp_data
    assert "baseline_plan" in comp_data
    assert "comparison" in comp_data
