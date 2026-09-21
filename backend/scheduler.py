"""Workflow scheduler for the Carbon- and Latency-Aware Agent Workflow Scheduler.

Coordinates data loading, invokes the optimization engine for each workflow task,
and aggregates individual scheduled steps into a complete ExecutionPlan.
Includes benchmark comparison against a highest-accuracy baseline.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.models import (
    ExecutionPlan,
    ExecutionWindow,
    ModelProfile,
    RegionProfile,
    ScheduledStep,
    WorkflowRequest,
    WorkflowTask,
)
from backend.optimizer import optimize_task, select_baseline_candidate


def _resolve_data_dir(custom_path: Optional[Path] = None) -> Path:
    """Resolve the directory containing mock data files.

    Checks:
    1. Explicit custom path if provided.
    2. Path relative to this file: ../data.
    3. Path relative to current working directory: ./data.
    """
    if custom_path is not None:
        return custom_path

    # Primary: relative to backend/ directory (parent.parent / "data")
    backend_data_dir = Path(__file__).resolve().parent.parent / "data"
    if backend_data_dir.exists() and backend_data_dir.is_dir():
        return backend_data_dir

    # Fallback: relative to current working directory
    cwd_data_dir = Path.cwd() / "data"
    if cwd_data_dir.exists() and cwd_data_dir.is_dir():
        return cwd_data_dir

    return backend_data_dir


def load_scheduler_data(
    data_dir: Optional[Path] = None,
) -> Tuple[List[ModelProfile], List[RegionProfile], Dict[str, List[ExecutionWindow]]]:
    """Load and parse simulated data from models.json, regions.json, and carbon.json.

    Args:
        data_dir: Optional path to the directory containing the data JSON files.

    Returns:
        A tuple of (models, regions, carbon_windows).

    Raises:
        RuntimeError: If any JSON file is missing, cannot be read, or fails schema validation.
    """
    resolved_dir = _resolve_data_dir(data_dir)

    models_file = resolved_dir / "models.json"
    regions_file = resolved_dir / "regions.json"
    carbon_file = resolved_dir / "carbon.json"

    # 1. Load and validate models.json
    try:
        if not models_file.is_file():
            raise FileNotFoundError(f"File not found: {models_file}")
        with open(models_file, "r", encoding="utf-8") as f:
            raw_models = json.load(f)
        if not isinstance(raw_models, list):
            raise ValueError("models.json content must be a JSON array")
        models = [ModelProfile.model_validate(m) for m in raw_models]
    except Exception as e:
        raise RuntimeError(f"Failed to load or parse models from '{models_file}': {e}") from e

    # 2. Load and validate regions.json
    try:
        if not regions_file.is_file():
            raise FileNotFoundError(f"File not found: {regions_file}")
        with open(regions_file, "r", encoding="utf-8") as f:
            raw_regions = json.load(f)
        if not isinstance(raw_regions, list):
            raise ValueError("regions.json content must be a JSON array")
        regions = [RegionProfile.model_validate(r) for r in raw_regions]
    except Exception as e:
        raise RuntimeError(f"Failed to load or parse regions from '{regions_file}': {e}") from e

    # 3. Load and validate carbon.json
    try:
        if not carbon_file.is_file():
            raise FileNotFoundError(f"File not found: {carbon_file}")
        with open(carbon_file, "r", encoding="utf-8") as f:
            raw_carbon = json.load(f)
        if not isinstance(raw_carbon, dict):
            raise ValueError("carbon.json content must be a JSON object mapping region_id to windows")
        carbon_windows: Dict[str, List[ExecutionWindow]] = {}
        for region_id, windows_list in raw_carbon.items():
            if not isinstance(windows_list, list):
                raise ValueError(f"Windows list for region '{region_id}' must be an array")
            carbon_windows[region_id] = [ExecutionWindow.model_validate(w) for w in windows_list]
    except Exception as e:
        raise RuntimeError(f"Failed to load or parse carbon windows from '{carbon_file}': {e}") from e

    return models, regions, carbon_windows


def schedule_workflow(
    workflow: Union[WorkflowRequest, dict],
    data_dir: Optional[Path] = None,
) -> ExecutionPlan:
    """Schedule every task in a WorkflowRequest independently into a complete ExecutionPlan.

    For every task in workflow.tasks, optimize_task() is invoked with:
    - the task
    - all available models from models.json
    - all available regions from regions.json
    - carbon windows from carbon.json
    - workflow importance weights (accuracy, latency, cost, carbon, energy)

    Args:
        workflow: The WorkflowRequest instance (or valid dict representation).
        data_dir: Optional path to directory with mock data JSON files.

    Returns:
        ExecutionPlan with all scheduled steps and overall cost, energy, and carbon totals.

    Raises:
        RuntimeError: If mock data files cannot be loaded or parsed.
        ValueError: If any task has no feasible execution option.
    """
    # Validate input with Pydantic if passed as dict
    if isinstance(workflow, dict):
        workflow = WorkflowRequest.model_validate(workflow)

    # Load mock data profiles
    models, regions, carbon_windows = load_scheduler_data(data_dir=data_dir)

    scheduled_steps: List[ScheduledStep] = []

    # Optimize each task independently using multi-objective scoring
    for task in workflow.tasks:
        scheduled_step = optimize_task(
            task=task,
            models=models,
            regions=regions,
            windows=carbon_windows,
            latency_importance=workflow.latency_importance,
            cost_importance=workflow.cost_importance,
            carbon_importance=workflow.carbon_importance,
            energy_importance=workflow.energy_importance,
            accuracy_importance=workflow.accuracy_importance,
        )
        scheduled_steps.append(scheduled_step)

    # Calculate aggregate totals
    total_cost = round(sum(step.estimated_cost for step in scheduled_steps), 6)
    total_energy_wh = round(sum(step.estimated_energy_wh for step in scheduled_steps), 6)
    total_carbon_g = round(sum(step.estimated_carbon_g for step in scheduled_steps), 6)

    return ExecutionPlan(
        workflow_id=workflow.workflow_id,
        total_estimated_cost=total_cost,
        total_estimated_energy_wh=total_energy_wh,
        total_estimated_carbon_g=total_carbon_g,
        scheduled_steps=scheduled_steps,
    )


def schedule_baseline_workflow(
    workflow: Union[WorkflowRequest, dict],
    data_dir: Optional[Path] = None,
) -> ExecutionPlan:
    """Schedule workflow tasks using the highest-accuracy feasible option benchmark heuristic.

    Strictly satisfies the same hard constraints (accuracy and deadline).

    Args:
        workflow: The WorkflowRequest instance (or valid dict representation).
        data_dir: Optional path to directory with mock data JSON files.

    Returns:
        ExecutionPlan representing the baseline schedule.

    Raises:
        RuntimeError: If mock data files cannot be loaded.
        ValueError: If any task has no feasible candidate.
    """
    if isinstance(workflow, dict):
        workflow = WorkflowRequest.model_validate(workflow)

    models, regions, carbon_windows = load_scheduler_data(data_dir=data_dir)
    scheduled_steps: List[ScheduledStep] = []

    for task in workflow.tasks:
        baseline_step = select_baseline_candidate(
            task=task,
            models=models,
            regions=regions,
            windows=carbon_windows,
        )
        scheduled_steps.append(baseline_step)

    total_cost = round(sum(step.estimated_cost for step in scheduled_steps), 6)
    total_energy_wh = round(sum(step.estimated_energy_wh for step in scheduled_steps), 6)
    total_carbon_g = round(sum(step.estimated_carbon_g for step in scheduled_steps), 6)

    return ExecutionPlan(
        workflow_id=workflow.workflow_id,
        total_estimated_cost=total_cost,
        total_estimated_energy_wh=total_energy_wh,
        total_estimated_carbon_g=total_carbon_g,
        scheduled_steps=scheduled_steps,
    )


def compare_workflow(
    workflow: Union[WorkflowRequest, dict],
    data_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Compare multi-objective optimized schedule against the highest-accuracy baseline schedule.

    Args:
        workflow: The WorkflowRequest instance.
        data_dir: Optional path to directory with mock data JSON files.

    Returns:
        Dictionary containing both plans and percentage/absolute savings.
    """
    if isinstance(workflow, dict):
        workflow = WorkflowRequest.model_validate(workflow)

    optimized_plan = schedule_workflow(workflow, data_dir=data_dir)
    baseline_plan = schedule_baseline_workflow(workflow, data_dir=data_dir)

    cost_saving = baseline_plan.total_estimated_cost - optimized_plan.total_estimated_cost
    energy_saving = baseline_plan.total_estimated_energy_wh - optimized_plan.total_estimated_energy_wh
    carbon_saving = baseline_plan.total_estimated_carbon_g - optimized_plan.total_estimated_carbon_g

    cost_pct = (cost_saving / baseline_plan.total_estimated_cost * 100.0) if baseline_plan.total_estimated_cost > 0 else 0.0
    energy_pct = (energy_saving / baseline_plan.total_estimated_energy_wh * 100.0) if baseline_plan.total_estimated_energy_wh > 0 else 0.0
    carbon_pct = (carbon_saving / baseline_plan.total_estimated_carbon_g * 100.0) if baseline_plan.total_estimated_carbon_g > 0 else 0.0

    return {
        "workflow_id": workflow.workflow_id,
        "optimized_plan": optimized_plan,
        "baseline_plan": baseline_plan,
        "comparison": {
            "cost_savings_pct": round(cost_pct, 2),
            "energy_savings_pct": round(energy_pct, 2),
            "carbon_savings_pct": round(carbon_pct, 2),
            "cost_delta": round(cost_saving, 6),
            "energy_delta_wh": round(energy_saving, 6),
            "carbon_delta_g": round(carbon_saving, 6),
        },
        "summary": (
            f"Optimized schedule achieves {carbon_pct:.1f}% estimated simulated carbon reduction "
            f"and {cost_pct:.1f}% estimated cost reduction relative to the highest-accuracy feasible baseline."
        ),
    }
