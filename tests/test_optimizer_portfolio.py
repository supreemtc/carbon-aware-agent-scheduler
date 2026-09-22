import pytest

from backend.models import ExecutionWindow, ModelProfile, RegionProfile, WorkflowTask
from backend.optimizer import optimize_task


def make_task(**overrides):
    data = {
        "step_id": "test",
        "task_type": "summarization",
        "description": "Test task",
        "input_text": "test",
        "estimated_tokens": 1000,
        "minimum_accuracy": 0.8,
        "deadline_seconds": 5,
        "delay_tolerance_seconds": 60,
        "priority": "normal",
    }
    data.update(overrides)
    return WorkflowTask(**data)


def test_infeasible_accuracy_is_rejected():
    models = [
        ModelProfile(
            model_id="weak",
            model_name="Weak",
            accuracy_score=0.70,
            average_latency_ms=100,
            cost_per_1k_tokens=0.1,
            energy_wh_per_1k_tokens=0.1,
            context_window=1000,
        )
    ]
    regions = [
        RegionProfile(
            region_id="r1",
            region_name="R1",
            base_latency_ms=10,
            carbon_intensity_gco2_kwh=100,
        )
    ]
    windows = [
        ExecutionWindow(
            window_id="w1",
            scheduled_offset_seconds=0,
            carbon_multiplier=1.0,
        )
    ]

    with pytest.raises(ValueError, match="No feasible execution plan"):
        optimize_task(make_task(minimum_accuracy=0.8), models, regions, windows)


def test_carbon_weight_prefers_clean_region():
    models = [
        ModelProfile(
            model_id="m",
            model_name="Model",
            accuracy_score=0.9,
            average_latency_ms=100,
            cost_per_1k_tokens=0.1,
            energy_wh_per_1k_tokens=0.1,
            context_window=1000,
        )
    ]
    regions = [
        RegionProfile(
            region_id="clean",
            region_name="Clean",
            base_latency_ms=10,
            carbon_intensity_gco2_kwh=10,
        ),
        RegionProfile(
            region_id="dirty",
            region_name="Dirty",
            base_latency_ms=10,
            carbon_intensity_gco2_kwh=1000,
        ),
    ]
    windows = {
        "clean": [
            ExecutionWindow(
                window_id="clean-now",
                scheduled_offset_seconds=0,
                carbon_multiplier=1.0,
            )
        ],
        "dirty": [
            ExecutionWindow(
                window_id="dirty-now",
                scheduled_offset_seconds=0,
                carbon_multiplier=1.0,
            )
        ],
    }

    result = optimize_task(
        make_task(),
        models,
        regions,
        windows,
        latency_importance=0.0,
        cost_importance=0.0,
        carbon_importance=1.0,
        energy_importance=0.0,
    )

    assert result.selected_region == "clean"
