"""Tests for Pydantic data models in backend/models.py."""

import pytest
from pydantic import ValidationError

from backend.models import (
    ExecutionPlan,
    ExecutionWindow,
    ModelProfile,
    RegionProfile,
    ScheduledStep,
    WorkflowRequest,
    WorkflowTask,
)


def test_valid_workflow_task():
    task = WorkflowTask(
        step_id="step-1",
        task_type="summarization",
        description="Summarize daily carbon emissions",
        input_text="Data on solar and wind generation...",
        estimated_tokens=1500,
        minimum_accuracy=0.85,
        deadline_seconds=120,
        delay_tolerance_seconds=30,
        priority="high",
    )
    assert task.step_id == "step-1"
    assert task.estimated_tokens == 1500
    assert task.minimum_accuracy == 0.85
    assert task.deadline_seconds == 120
    assert task.delay_tolerance_seconds == 30
    assert task.priority == "high"


def test_valid_workflow_request():
    task = WorkflowTask(
        step_id="step-1",
        task_type="summarization",
        description="Summarize",
        input_text="Sample input",
        estimated_tokens=500,
        minimum_accuracy=0.8,
        deadline_seconds=60,
        delay_tolerance_seconds=10,
        priority="normal",
    )
    request = WorkflowRequest(
        workflow_id="wf-001",
        tasks=[task],
        latency_importance=0.4,
        cost_importance=0.2,
        carbon_importance=0.8,
        energy_importance=0.3,
    )
    assert request.workflow_id == "wf-001"
    assert len(request.tasks) == 1
    assert request.latency_importance == 0.4
    assert request.carbon_importance == 0.8


def test_valid_model_profile():
    model = ModelProfile(
        model_id="gemini-1.5-flash",
        model_name="Gemini 1.5 Flash",
        accuracy_score=0.85,
        average_latency_ms=350.0,
        cost_per_1k_tokens=0.00015,
        energy_wh_per_1k_tokens=0.05,
        context_window=1000000,
    )
    assert model.model_id == "gemini-1.5-flash"
    assert model.context_window == 1000000
    assert model.accuracy_score == 0.85


def test_valid_region_profile():
    region = RegionProfile(
        region_id="europe-north1",
        region_name="Europe North (Finland)",
        base_latency_ms=140.0,
        carbon_intensity_gco2_kwh=35.0,
    )
    assert region.region_id == "europe-north1"
    assert region.carbon_intensity_gco2_kwh == 35.0


def test_valid_execution_window():
    window = ExecutionWindow(
        window_id="win-15s",
        scheduled_offset_seconds=15,
        carbon_multiplier=0.85,
    )
    assert window.scheduled_offset_seconds == 15
    assert window.carbon_multiplier == 0.85


def test_valid_scheduled_step():
    step = ScheduledStep(
        step_id="step-1",
        selected_model="gemini-1.5-flash",
        selected_region="europe-north1",
        scheduled_offset_seconds=15,
        estimated_latency_ms=490.0,
        estimated_accuracy=0.85,
        estimated_cost=0.00015,
        estimated_energy_wh=0.05,
        estimated_carbon_g=0.00148,
        score=0.12,
        reason="Selected optimal green candidate.",
    )
    assert step.selected_model == "gemini-1.5-flash"
    assert step.selected_region == "europe-north1"
    assert step.score == 0.12


def test_valid_execution_plan():
    step = ScheduledStep(
        step_id="step-1",
        selected_model="gemini-1.5-flash",
        selected_region="europe-north1",
        scheduled_offset_seconds=15,
        estimated_latency_ms=490.0,
        estimated_accuracy=0.85,
        estimated_cost=0.00015,
        estimated_energy_wh=0.05,
        estimated_carbon_g=0.00148,
        score=0.12,
        reason="Selected optimal candidate.",
    )
    plan = ExecutionPlan(
        workflow_id="wf-001",
        total_estimated_cost=0.00015,
        total_estimated_energy_wh=0.05,
        total_estimated_carbon_g=0.00148,
        scheduled_steps=[step],
    )
    assert plan.workflow_id == "wf-001"
    assert len(plan.scheduled_steps) == 1
    assert plan.total_estimated_cost == 0.00015


@pytest.mark.parametrize("invalid_tokens", [0, -1, -500])
def test_workflow_task_invalid_estimated_tokens(invalid_tokens):
    with pytest.raises(ValidationError):
        WorkflowTask(
            step_id="step-err",
            task_type="test",
            description="desc",
            input_text="input",
            estimated_tokens=invalid_tokens,
            minimum_accuracy=0.8,
            deadline_seconds=60,
            delay_tolerance_seconds=0,
            priority="normal",
        )


@pytest.mark.parametrize("invalid_acc", [-0.1, 1.05, 2.0])
def test_workflow_task_invalid_minimum_accuracy(invalid_acc):
    with pytest.raises(ValidationError):
        WorkflowTask(
            step_id="step-err",
            task_type="test",
            description="desc",
            input_text="input",
            estimated_tokens=1000,
            minimum_accuracy=invalid_acc,
            deadline_seconds=60,
            delay_tolerance_seconds=0,
            priority="normal",
        )


@pytest.mark.parametrize("invalid_deadline", [0, -1, -100])
def test_workflow_task_invalid_deadline_seconds(invalid_deadline):
    with pytest.raises(ValidationError):
        WorkflowTask(
            step_id="step-err",
            task_type="test",
            description="desc",
            input_text="input",
            estimated_tokens=1000,
            minimum_accuracy=0.8,
            deadline_seconds=invalid_deadline,
            delay_tolerance_seconds=0,
            priority="normal",
        )


@pytest.mark.parametrize(
    "lat,cost,carbon,energy",
    [
        (1.5, 0.5, 0.5, 0.5),
        (-0.1, 0.5, 0.5, 0.5),
        (0.5, 1.2, 0.5, 0.5),
        (0.5, 0.5, -0.2, 0.5),
        (0.5, 0.5, 0.5, 2.0),
    ],
)
def test_workflow_request_invalid_importance(lat, cost, carbon, energy):
    task = WorkflowTask(
        step_id="step-1",
        task_type="test",
        description="desc",
        input_text="input",
        estimated_tokens=100,
        minimum_accuracy=0.5,
        deadline_seconds=10,
        delay_tolerance_seconds=0,
        priority="low",
    )
    with pytest.raises(ValidationError):
        WorkflowRequest(
            workflow_id="wf-err",
            tasks=[task],
            latency_importance=lat,
            cost_importance=cost,
            carbon_importance=carbon,
            energy_importance=energy,
        )


def test_workflow_request_empty_tasks():
    with pytest.raises(ValidationError):
        WorkflowRequest(
            workflow_id="wf-empty",
            tasks=[],
            latency_importance=0.5,
            cost_importance=0.5,
            carbon_importance=0.5,
            energy_importance=0.5,
        )


@pytest.mark.parametrize("invalid_acc", [-0.01, 1.05, 2.5])
def test_model_profile_invalid_accuracy(invalid_acc):
    with pytest.raises(ValidationError):
        ModelProfile(
            model_id="test-model",
            model_name="Test Model",
            accuracy_score=invalid_acc,
            average_latency_ms=100.0,
            cost_per_1k_tokens=0.001,
            energy_wh_per_1k_tokens=0.01,
            context_window=10000,
        )


@pytest.mark.parametrize("invalid_multiplier", [0.0, -0.5, -1.0])
def test_execution_window_invalid_multiplier(invalid_multiplier):
    with pytest.raises(ValidationError):
        ExecutionWindow(
            window_id="win-err",
            scheduled_offset_seconds=10,
            carbon_multiplier=invalid_multiplier,
        )
