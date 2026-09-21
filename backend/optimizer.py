"""Deterministic optimization engine for agent workflow scheduling.

Evaluates combinations of Gemini models, compute regions, and execution time windows
to find the optimal Pareto trade-off among accuracy, latency, cost, energy, and carbon emissions
while strictly satisfying task constraints. Includes baseline candidate selection for benchmark comparisons.
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
    """Normalize a metric to [0.0, 1.0] where 0.0 is the minimum and 1.0 is the maximum.

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
    latency_importance: float = 0.20,
    cost_importance: float = 0.20,
    carbon_importance: float = 0.15,
    energy_importance: float = 0.15,
    accuracy_importance: float = 0.30,
    request: Optional[WorkflowRequest] = None,
) -> ScheduledStep:
    """Select the optimal model, region, and execution window for a single workflow task.

    Incorporates Person 2's multi-objective decision framework:
    1. Filter out candidates failing hard constraints:
       - accuracy >= task.minimum_accuracy
       - latency <= task.deadline_seconds * 1000
    2. Normalize cost/latency/energy/carbon metrics across feasible candidates.
    3. Calculate composite utility score:
       - Accuracy is a positive contribution (higher improves score).
       - Latency, cost, energy, and carbon are negative contributions (lower improves score via 1 - norm).
    4. Select the candidate maximizing the multi-objective utility score.

    Args:
        task: The task specification containing constraints and token estimates.
        models: Available AI model profiles.
        regions: Available compute region profiles.
        windows: Execution windows (either a list or a dict mapping region_id to windows).
        latency_importance: Weight for minimizing latency (0.0 to 1.0, default 0.20).
        cost_importance: Weight for minimizing cost (0.0 to 1.0, default 0.20).
        carbon_importance: Weight for minimizing carbon emissions (0.0 to 1.0, default 0.15).
        energy_importance: Weight for minimizing energy consumption (0.0 to 1.0, default 0.15).
        accuracy_importance: Weight for maximizing accuracy (0.0 to 1.0, default 0.30).
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
        accuracy_importance = getattr(request, "accuracy_importance", 0.30)

    # Normalize weights safely; if all weights are zero, use default prototype weights:
    # accuracy=0.30, latency=0.20, cost=0.20, energy=0.15, carbon=0.15
    total_weights = (
        accuracy_importance
        + latency_importance
        + cost_importance
        + carbon_importance
        + energy_importance
    )
    if total_weights <= 0.0:
        w_acc = 0.30
        w_lat = 0.20
        w_cost = 0.20
        w_energy = 0.15
        w_carbon = 0.15
    else:
        w_acc = accuracy_importance / total_weights
        w_lat = latency_importance / total_weights
        w_cost = cost_importance / total_weights
        w_energy = energy_importance / total_weights
        w_carbon = carbon_importance / total_weights

    deadline_ms = task.deadline_seconds * 1000.0
    feasible_candidates: List[_CandidateEvaluation] = []

    # Step 1: Evaluate all combinations of Model, Region, and ExecutionWindow
    for model in models:
        for region in regions:
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

                # Step 4: Check hard feasibility constraints
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

    # If no candidate satisfies constraints, raise ValueError
    if not feasible_candidates:
        raise ValueError(
            f"No feasible execution plan exists for task '{task.step_id}'. "
            f"No candidate satisfies accuracy >= {task.minimum_accuracy} "
            f"and latency <= {deadline_ms:.1f}ms."
        )

    # Step 6: Calculate min and max for normalization across feasible candidates
    min_lat = min(c.estimated_latency_ms for c in feasible_candidates)
    max_lat = max(c.estimated_latency_ms for c in feasible_candidates)

    min_cost = min(c.estimated_cost for c in feasible_candidates)
    max_cost = max(c.estimated_cost for c in feasible_candidates)

    min_energy = min(c.estimated_energy for c in feasible_candidates)
    max_energy = max(c.estimated_energy for c in feasible_candidates)

    min_carbon = min(c.estimated_carbon for c in feasible_candidates)
    max_carbon = max(c.estimated_carbon for c in feasible_candidates)

    # Calculate multi-objective utility score (higher is better)
    for cand in feasible_candidates:
        # Accuracy contributes positively (already in 0-1 range)
        utility_acc = cand.estimated_accuracy

        # Latency, cost, energy, and carbon contribute positively via (1 - norm)
        norm_lat = _normalize(cand.estimated_latency_ms, min_lat, max_lat)
        utility_lat = 1.0 - norm_lat

        norm_cost = _normalize(cand.estimated_cost, min_cost, max_cost)
        utility_cost = 1.0 - norm_cost

        norm_energy = _normalize(cand.estimated_energy, min_energy, max_energy)
        utility_energy = 1.0 - norm_energy

        norm_carbon = _normalize(cand.estimated_carbon, min_carbon, max_carbon)
        utility_carbon = 1.0 - norm_carbon

        cand.score = (
            w_acc * utility_acc
            + w_lat * utility_lat
            + w_cost * utility_cost
            + w_energy * utility_energy
            + w_carbon * utility_carbon
        )

    # Deterministic selection: sort by score descending, then tie-break
    feasible_candidates.sort(
        key=lambda c: (
            c.score,
            c.estimated_accuracy,
            -c.estimated_carbon,
            -c.estimated_latency_ms,
            -c.estimated_cost,
            c.model.model_id,
            c.region.region_id,
            -c.window.scheduled_offset_seconds,
        ),
        reverse=True,
    )

    best = feasible_candidates[0]

    # Human-readable explanation of selection rationale
    reason = (
        f"Selected {best.model.model_id} in {best.region.region_id} at "
        f"+{best.window.scheduled_offset_seconds}s because it satisfies the accuracy and "
        f"latency constraints and provides the best weighted trade-off across "
        f"accuracy, latency, cost, energy, and carbon."
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


def select_baseline_candidate(
    task: WorkflowTask,
    models: List[ModelProfile],
    regions: List[RegionProfile],
    windows: Union[List[ExecutionWindow], Dict[str, List[ExecutionWindow]]],
) -> ScheduledStep:
    """Select the highest-accuracy feasible option as a fair benchmark baseline.

    The baseline obeys the exact same hard constraints (minimum accuracy and deadline).
    Ties in accuracy prioritize immediate execution (offset=0), lower latency, and lower cost.

    Args:
        task: The task specification containing constraints and token estimates.
        models: Available AI model profiles.
        regions: Available compute region profiles.
        windows: Execution windows (either a list or a dict mapping region_id to windows).

    Returns:
        ScheduledStep containing the baseline execution candidate.

    Raises:
        ValueError: If no feasible execution plan exists for the task.
    """
    if not models or not regions or not windows:
        raise ValueError("Models, regions, and execution windows must all be non-empty.")

    deadline_ms = task.deadline_seconds * 1000.0
    feasible_candidates: List[_CandidateEvaluation] = []

    for model in models:
        for region in regions:
            if isinstance(windows, dict):
                region_windows = windows.get(region.region_id, [])
            else:
                region_windows = windows

            for window in region_windows:
                estimated_latency_ms = model.average_latency_ms + region.base_latency_ms
                estimated_accuracy = model.accuracy_score
                estimated_cost = (task.estimated_tokens / 1000.0) * model.cost_per_1k_tokens
                estimated_energy = (task.estimated_tokens / 1000.0) * model.energy_wh_per_1k_tokens
                estimated_carbon = (
                    (estimated_energy * region.carbon_intensity_gco2_kwh / 1000.0)
                    * window.carbon_multiplier
                )

                # Hard constraints must be satisfied
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

    if not feasible_candidates:
        raise ValueError(
            f"No feasible execution plan exists for task '{task.step_id}'. "
            f"No candidate satisfies accuracy >= {task.minimum_accuracy} "
            f"and latency <= {deadline_ms:.1f}ms."
        )

    # Baseline selects highest accuracy feasible option, preferring immediate execution (offset=0)
    feasible_candidates.sort(
        key=lambda c: (
            c.estimated_accuracy,
            -c.window.scheduled_offset_seconds,
            -c.estimated_latency_ms,
            -c.estimated_cost,
            -c.estimated_carbon,
            c.model.model_id,
            c.region.region_id,
        ),
        reverse=True,
    )

    best = feasible_candidates[0]

    reason = (
        f"Selected highest-accuracy feasible baseline: {best.model.model_id} in "
        f"{best.region.region_id} at +{best.window.scheduled_offset_seconds}s "
        f"(accuracy: {best.estimated_accuracy:.4f}, latency: {best.estimated_latency_ms:.1f}ms)."
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
        score=round(best.estimated_accuracy, 6),
        reason=reason,
    )
