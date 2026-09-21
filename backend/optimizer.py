"""Deterministic optimization engine for agent workflow scheduling.

Evaluates combinations of Gemini models, compute regions, and execution time windows
to find the optimal Pareto trade-off between latency, cost, energy, and carbon emissions
while strictly satisfying task constraints.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from backend.models import (
    ExecutionWindow,
    ModelProfile,
    RegionProfile,
    ScheduledStep,
    WorkflowRequest,
    WorkflowTask,
)


@dataclass
class _CandidateEvaluation:
    """Internal container for evaluated execution candidates."""

    model: ModelProfile
    region: RegionProfile
    window: ExecutionWindow
    estimated_latency_ms: float
    estimated_accuracy: float
    estimated_cost: float
    estimated_energy: float
    estimated_carbon: float
    score: float = 0.0


def _normalize(value: float, min_val: float, max_val: float) -> float:
    """Normalize a metric to [0.0, 1.0] where lower is better.

    If all candidates have the same value, returns 0.0 to prevent division by zero.
    """
    diff = max_val - min_val
    if abs(diff) < 1e-9:
        return 0.0
    return (value - min_val) / diff


def optimize_task(
    task: WorkflowTask,
    models: List[ModelProfile],
    regions: List[RegionProfile],
    windows: Union[List[ExecutionWindow], Dict[str, List[ExecutionWindow]]],
    latency_importance: float = 0.25,
    cost_importance: float = 0.25,
    carbon_importance: float = 0.25,
    energy_importance: float = 0.25,
    request: Optional[WorkflowRequest] = None,
) -> ScheduledStep:
    """Select the optimal model, region, and execution window for a single workflow task.

    Args:
        task: The task specification containing constraints and token estimates.
        models: Available AI model profiles.
        regions: Available compute region profiles.
        windows: Execution windows (either a list or a dict mapping region_id to windows).
        latency_importance: Weight for minimizing latency (0.0 to 1.0).
        cost_importance: Weight for minimizing cost (0.0 to 1.0).
        carbon_importance: Weight for minimizing carbon emissions (0.0 to 1.0).
        energy_importance: Weight for minimizing energy consumption (0.0 to 1.0).
        request: Optional WorkflowRequest to inherit optimization weights from.

    Returns:
        ScheduledStep containing the selected assignment, metrics, score, and explanation.

    Raises:
        ValueError: If inputs are invalid or no candidate satisfies the feasibility constraints.
    """
    if not models:
        raise ValueError("At least one ModelProfile must be provided.")
    if not regions:
        raise ValueError("At least one RegionProfile must be provided.")
    if not windows:
        raise ValueError("At least one ExecutionWindow must be provided.")

    # Inherit importance weights from WorkflowRequest if provided
    if request is not None:
        latency_importance = request.latency_importance
        cost_importance = request.cost_importance
        carbon_importance = request.carbon_importance
        energy_importance = request.energy_importance

    # Fall back to equal weights if all provided weights are zero
    total_weights = latency_importance + cost_importance + carbon_importance + energy_importance
    if total_weights <= 0.0:
        latency_importance = 0.25
        cost_importance = 0.25
        carbon_importance = 0.25
        energy_importance = 0.25

    deadline_ms = task.deadline_seconds * 1000.0
    feasible_candidates: List[_CandidateEvaluation] = []

    # Step 1: Evaluate all combinations of Model, Region, and ExecutionWindow
    for model in models:
        for region in regions:
            # Resolve execution windows for this specific region
            if isinstance(windows, dict):
                region_windows = windows.get(region.region_id, [])
            else:
                region_windows = windows

            for window in region_windows:
                # 1. Latency: model inference latency + network latency
                estimated_latency_ms = model.average_latency_ms + region.base_latency_ms

                # 2. Accuracy: baseline benchmark accuracy of the selected model
                estimated_accuracy = model.accuracy_score

                # 3. Cost: linear scaling with estimated tokens
                estimated_cost = (task.estimated_tokens / 1000.0) * model.cost_per_1k_tokens

                # 4. Energy: estimated energy consumption in Watt-hours
                estimated_energy = (task.estimated_tokens / 1000.0) * model.energy_wh_per_1k_tokens

                # 5. Carbon: energy (kWh) * grid carbon intensity * window temporal multiplier
                estimated_carbon = (
                    (estimated_energy * region.carbon_intensity_gco2_kwh / 1000.0)
                    * window.carbon_multiplier
                )

                # Step 3: Check feasibility constraints
                if estimated_accuracy < task.minimum_accuracy:
                    continue
                if estimated_latency_ms > deadline_ms:
                    continue

                feasible_candidates.append(
                    _CandidateEvaluation(
                        model=model,
                        region=region,
                        window=window,
                        estimated_latency_ms=estimated_latency_ms,
                        estimated_accuracy=estimated_accuracy,
                        estimated_cost=estimated_cost,
                        estimated_energy=estimated_energy,
                        estimated_carbon=estimated_carbon,
                    )
                )

    # Step 6: If no candidate satisfies constraints, raise ValueError
    if not feasible_candidates:
        raise ValueError(
            f"No feasible execution plan exists for task '{task.step_id}'. "
            f"No candidate satisfies accuracy >= {task.minimum_accuracy} "
            f"and latency <= {deadline_ms:.1f}ms."
        )

    # Step 4: Calculate min and max for normalization across feasible candidates
    min_lat = min(c.estimated_latency_ms for c in feasible_candidates)
    max_lat = max(c.estimated_latency_ms for c in feasible_candidates)

    min_cost = min(c.estimated_cost for c in feasible_candidates)
    max_cost = max(c.estimated_cost for c in feasible_candidates)

    min_energy = min(c.estimated_energy for c in feasible_candidates)
    max_energy = max(c.estimated_energy for c in feasible_candidates)

    min_carbon = min(c.estimated_carbon for c in feasible_candidates)
    max_carbon = max(c.estimated_carbon for c in feasible_candidates)

    # Calculate normalized weighted score for each candidate (lower is better)
    for cand in feasible_candidates:
        norm_lat = _normalize(cand.estimated_latency_ms, min_lat, max_lat)
        norm_cost = _normalize(cand.estimated_cost, min_cost, max_cost)
        norm_energy = _normalize(cand.estimated_energy, min_energy, max_energy)
        norm_carbon = _normalize(cand.estimated_carbon, min_carbon, max_carbon)

        cand.score = (
            latency_importance * norm_lat
            + cost_importance * norm_cost
            + carbon_importance * norm_carbon
            + energy_importance * norm_energy
        )

    # Deterministic selection: sort by score, then tie-break on carbon, latency, cost, and IDs
    feasible_candidates.sort(
        key=lambda c: (
            c.score,
            c.estimated_carbon,
            c.estimated_latency_ms,
            c.estimated_cost,
            c.model.model_id,
            c.region.region_id,
            c.window.scheduled_offset_seconds,
        )
    )

    best = feasible_candidates[0]

    # Human-readable explanation of selection rationale
    reason = (
        f"Selected {best.model.model_id} in {best.region.region_id} at "
        f"+{best.window.scheduled_offset_seconds}s because it provides the best weighted "
        f"trade-off among latency, cost, energy, and carbon while satisfying the task constraints."
    )

    return ScheduledStep(
        step_id=task.step_id,
        selected_model=best.model.model_id,
        selected_region=best.region.region_id,
        scheduled_offset_seconds=best.window.scheduled_offset_seconds,
        estimated_latency_ms=round(best.estimated_latency_ms, 2),
        estimated_accuracy=round(best.estimated_accuracy, 4),
        estimated_cost=round(best.estimated_cost, 6),
        estimated_energy_wh=round(best.estimated_energy, 6),
        estimated_carbon_g=round(best.estimated_carbon, 6),
        score=round(best.score, 6),
        reason=reason,
    )
