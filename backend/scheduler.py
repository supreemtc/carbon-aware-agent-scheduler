"""Workflow scheduler for the Carbon- and Latency-Aware Agent Workflow Scheduler.

Coordinates data loading, invokes the optimization engine for each workflow task,
and aggregates individual scheduled steps into a complete ExecutionPlan.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from backend.models import (
    ExecutionPlan,
    ExecutionWindow,
    ModelProfile,
    RegionProfile,
    ScheduledStep,
    WorkflowRequest,
    WorkflowTask,
)
from backend.optimizer import optimize_task


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
    - workflow importance weights (latency, cost, carbon, energy)

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

    # Optimize each task independently
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
