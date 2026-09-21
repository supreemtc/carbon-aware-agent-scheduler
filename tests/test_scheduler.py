"""Tests for the workflow scheduler in backend/scheduler.py."""

from pathlib import Path
import pytest
from pydantic import ValidationError

from backend.models import (
    ExecutionPlan,
    ScheduledStep,
    WorkflowRequest,
    WorkflowTask,
)
from backend.scheduler import load_scheduler_data, schedule_workflow


def test_loading_json_datasets():
    models, regions, windows = load_scheduler_data()
    assert len(models) == 3
    assert len(regions) == 4
    assert len(windows) == 4
    for r in regions:
        assert r.region_id in windows


@pytest.fixture
def multi_task_workflow():
    task1 = WorkflowTask(
        step_id="step-1-parse",
        task_type="parsing",
        description="Parse carbon logs",
        input_text="Log contents...",
        estimated_tokens=1000,
        minimum_accuracy=0.75,
        deadline_seconds=3,
        delay_tolerance_seconds=15,
        priority="normal",
    )
    task2 = WorkflowTask(
        step_id="step-2-model",
        task_type="modeling",
        description="Run forecasting",
        input_text="Model input features...",
        estimated_tokens=2000,
        minimum_accuracy=0.85,
        deadline_seconds=4,
        delay_tolerance_seconds=30,
        priority="high",
    )
    return WorkflowRequest(
        workflow_id="wf-multi-001",
        tasks=[task1, task2],
        latency_importance=0.25,
        cost_importance=0.25,
        carbon_importance=0.25,
        energy_importance=0.25,
    )


def test_scheduling_valid_multi_task_workflow(multi_task_workflow):
    plan = schedule_workflow(multi_task_workflow)
    assert isinstance(plan, ExecutionPlan)


def test_correct_number_of_scheduled_steps(multi_task_workflow):
    plan = schedule_workflow(multi_task_workflow)
    assert len(plan.scheduled_steps) == 2
    for step in plan.scheduled_steps:
        assert isinstance(step, ScheduledStep)


def test_correct_aggregation_of_cost(multi_task_workflow):
    plan = schedule_workflow(multi_task_workflow)
    expected_cost = round(sum(s.estimated_cost for s in plan.scheduled_steps), 6)
    assert abs(plan.total_estimated_cost - expected_cost) < 1e-9


def test_correct_aggregation_of_energy(multi_task_workflow):
    plan = schedule_workflow(multi_task_workflow)
    expected_energy = round(sum(s.estimated_energy_wh for s in plan.scheduled_steps), 6)
    assert abs(plan.total_estimated_energy_wh - expected_energy) < 1e-9


def test_correct_aggregation_of_carbon(multi_task_workflow):
    plan = schedule_workflow(multi_task_workflow)
    expected_carbon = round(sum(s.estimated_carbon_g for s in plan.scheduled_steps), 6)
    assert abs(plan.total_estimated_carbon_g - expected_carbon) < 1e-9


def test_workflow_id_is_preserved(multi_task_workflow):
    plan = schedule_workflow(multi_task_workflow)
    assert plan.workflow_id == multi_task_workflow.workflow_id


def test_missing_dataset_path_raises_runtime_error():
    invalid_path = Path("/non/existent/path/to/data")
    with pytest.raises(RuntimeError, match="Failed to load or parse"):
        load_scheduler_data(data_dir=invalid_path)


def test_infeasible_task_propagates_value_error():
    infeasible_task = WorkflowTask(
        step_id="step-infeasible",
        task_type="impossible",
        description="Impossible task",
        input_text="data",
        estimated_tokens=500,
        minimum_accuracy=0.999,  # No model reaches 0.999
        deadline_seconds=1,
        delay_tolerance_seconds=0,
        priority="high",
    )
    workflow = WorkflowRequest(
        workflow_id="wf-fail",
        tasks=[infeasible_task],
        latency_importance=0.25,
        cost_importance=0.25,
        carbon_importance=0.25,
        energy_importance=0.25,
    )
    with pytest.raises(ValueError, match="No feasible execution plan exists"):
        schedule_workflow(workflow)


def test_empty_workflow_is_rejected_by_pydantic():
    with pytest.raises(ValidationError):
        WorkflowRequest(
            workflow_id="wf-empty",
            tasks=[],
            latency_importance=0.25,
            cost_importance=0.25,
            carbon_importance=0.25,
            energy_importance=0.25,
        )
