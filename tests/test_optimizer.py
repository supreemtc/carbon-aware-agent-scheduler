"""Tests for the deterministic optimization engine in backend/optimizer.py."""

import pytest

from backend.models import (
    ExecutionWindow,
    ModelProfile,
    RegionProfile,
    ScheduledStep,
    WorkflowTask,
)
from backend.optimizer import optimize_task


@pytest.fixture
def sample_models():
    return [
        ModelProfile(
            model_id="gemini-1.5-flash",
            model_name="Gemini 1.5 Flash",
            accuracy_score=0.85,
            average_latency_ms=350.0,
            cost_per_1k_tokens=0.00015,
            energy_wh_per_1k_tokens=0.05,
            context_window=1000000,
        ),
        ModelProfile(
            model_id="gemini-1.5-pro",
            model_name="Gemini 1.5 Pro",
            accuracy_score=0.92,
            average_latency_ms=1200.0,
            cost_per_1k_tokens=0.00125,
            energy_wh_per_1k_tokens=0.18,
            context_window=2000000,
        ),
    ]


@pytest.fixture
def sample_regions():
    return [
        RegionProfile(
            region_id="asia-south1",
            region_name="Mumbai",
            base_latency_ms=25.0,
            carbon_intensity_gco2_kwh=580.0,
        ),
        RegionProfile(
            region_id="europe-north1",
            region_name="Finland",
            base_latency_ms=140.0,
            carbon_intensity_gco2_kwh=35.0,
        ),
    ]


@pytest.fixture
def sample_windows():
    return [
        ExecutionWindow(
            window_id="win-0s",
            scheduled_offset_seconds=0,
            carbon_multiplier=1.0,
        ),
        ExecutionWindow(
            window_id="win-15s",
            scheduled_offset_seconds=15,
            carbon_multiplier=0.85,
        ),
    ]


@pytest.fixture
def standard_task():
    return WorkflowTask(
        step_id="step-test",
        task_type="classification",
        description="Classify incoming feedback",
        input_text="Sample feedback text...",
        estimated_tokens=2000,
        minimum_accuracy=0.80,
        deadline_seconds=2,  # 2000 ms
        delay_tolerance_seconds=15,
        priority="normal",
    )


def test_normal_feasible_optimization(standard_task, sample_models, sample_regions, sample_windows):
    step = optimize_task(
        task=standard_task,
        models=sample_models,
        regions=sample_regions,
        windows=sample_windows,
        latency_importance=0.25,
        cost_importance=0.25,
        carbon_importance=0.25,
        energy_importance=0.25,
    )
    assert isinstance(step, ScheduledStep)
    assert step.step_id == standard_task.step_id
    assert step.estimated_accuracy >= standard_task.minimum_accuracy
    assert step.estimated_latency_ms <= standard_task.deadline_seconds * 1000
    assert step.score >= 0.0
    assert "Selected" in step.reason


def test_carbon_heavy_weighting_selects_low_carbon(
    standard_task, sample_models, sample_regions, sample_windows
):
    step = optimize_task(
        task=standard_task,
        models=sample_models,
        regions=sample_regions,
        windows=sample_windows,
        latency_importance=0.0,
        cost_importance=0.0,
        carbon_importance=1.0,
        energy_importance=0.0,
    )
    # europe-north1 has significantly lower carbon (35 vs 580) and offset 15s has 0.85 multiplier
    assert step.selected_region == "europe-north1"
    assert step.scheduled_offset_seconds == 15


def test_latency_heavy_weighting_selects_low_latency(
    standard_task, sample_models, sample_regions, sample_windows
):
    step = optimize_task(
        task=standard_task,
        models=sample_models,
        regions=sample_regions,
        windows=sample_windows,
        latency_importance=1.0,
        cost_importance=0.0,
        carbon_importance=0.0,
        energy_importance=0.0,
    )
    # asia-south1 has lowest latency (25ms vs 140ms) and flash is fastest (350ms vs 1200ms)
    assert step.selected_model == "gemini-1.5-flash"
    assert step.selected_region == "asia-south1"


def test_all_weights_zero_falls_back_to_equal_weights(
    standard_task, sample_models, sample_regions, sample_windows
):
    step = optimize_task(
        task=standard_task,
        models=sample_models,
        regions=sample_regions,
        windows=sample_windows,
        latency_importance=0.0,
        cost_importance=0.0,
        carbon_importance=0.0,
        energy_importance=0.0,
    )
    assert isinstance(step, ScheduledStep)
    assert step.score >= 0.0


def test_impossible_accuracy_requirement_raises_value_error(
    sample_models, sample_regions, sample_windows
):
    task = WorkflowTask(
        step_id="step-impossible-acc",
        task_type="proof",
        description="Requires 99.9% accuracy",
        input_text="Impossible theorem",
        estimated_tokens=500,
        minimum_accuracy=0.999,  # Highest model accuracy is 0.92
        deadline_seconds=10,
        delay_tolerance_seconds=0,
        priority="high",
    )
    with pytest.raises(ValueError, match="No feasible execution plan exists"):
        optimize_task(
            task=task,
            models=sample_models,
            regions=sample_regions,
            windows=sample_windows,
        )


def test_impossible_deadline_raises_value_error(
    sample_models, sample_regions, sample_windows
):
    # Pro model has 1200ms average latency + 25ms base latency = 1225ms,
    # which exceeds the 1-second (1000ms) hard deadline.
    fast_task = WorkflowTask(
        step_id="step-impossible-lat",
        task_type="fast_query",
        description="Requires tight deadline",
        input_text="Query",
        estimated_tokens=500,
        minimum_accuracy=0.5,
        deadline_seconds=1,  # 1000ms
        delay_tolerance_seconds=0,
        priority="high",
    )
    slow_models = [sample_models[1]]
    with pytest.raises(ValueError, match="No feasible execution plan exists"):
        optimize_task(
            task=fast_task,
            models=slow_models,
            regions=sample_regions,
            windows=sample_windows,
        )


def test_single_candidate_works(standard_task, sample_models, sample_regions, sample_windows):
    single_model = [sample_models[0]]
    single_region = [sample_regions[0]]
    single_window = [sample_windows[0]]

    step = optimize_task(
        task=standard_task,
        models=single_model,
        regions=single_region,
        windows=single_window,
    )
    assert isinstance(step, ScheduledStep)
    assert step.selected_model == single_model[0].model_id
    assert step.selected_region == single_region[0].region_id
    assert step.score == 0.0


def test_identical_metric_values_do_not_cause_division_by_zero(standard_task):
    identical_models = [
        ModelProfile(
            model_id="m1",
            model_name="Model 1",
            accuracy_score=0.9,
            average_latency_ms=100.0,
            cost_per_1k_tokens=0.01,
            energy_wh_per_1k_tokens=0.05,
            context_window=5000,
        ),
        ModelProfile(
            model_id="m2",
            model_name="Model 2",
            accuracy_score=0.9,
            average_latency_ms=100.0,
            cost_per_1k_tokens=0.01,
            energy_wh_per_1k_tokens=0.05,
            context_window=5000,
        ),
    ]
    identical_regions = [
        RegionProfile(
            region_id="r1",
            region_name="Region 1",
            base_latency_ms=20.0,
            carbon_intensity_gco2_kwh=100.0,
        ),
    ]
    identical_windows = [
        ExecutionWindow(
            window_id="w1",
            scheduled_offset_seconds=0,
            carbon_multiplier=1.0,
        ),
    ]

    step = optimize_task(
        task=standard_task,
        models=identical_models,
        regions=identical_regions,
        windows=identical_windows,
    )
    assert isinstance(step, ScheduledStep)
    assert step.score == 0.0
