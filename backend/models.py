"""Pydantic data models for the Carbon- and Latency-Aware Agent Workflow Scheduler.

Defines schemas and validation rules for tasks, requests, model profiles,
region profiles, execution windows, scheduled steps, and execution plans.
"""

from typing import List
from pydantic import BaseModel, Field


class WorkflowTask(BaseModel):
    """Specification of an individual task within an agent workflow."""

    step_id: str = Field(..., description="Unique identifier for the step")
    task_type: str = Field(..., description="Type of task (e.g., summarization, reasoning, code)")
    description: str = Field(..., description="Human-readable description of the task")
    input_text: str = Field(..., description="Input prompt or payload for the task")
    estimated_tokens: int = Field(..., gt=0, description="Estimated total token count (must be > 0)")
    minimum_accuracy: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Minimum acceptable accuracy score between 0.0 and 1.0",
    )
    deadline_seconds: int = Field(..., gt=0, description="Hard deadline in seconds (must be > 0)")
    delay_tolerance_seconds: int = Field(
        ...,
        ge=0,
        description="Acceptable delay in seconds for carbon shifting (must be >= 0)",
    )
    priority: str = Field(..., description="Priority level of the task (e.g., low, normal, high)")


class WorkflowRequest(BaseModel):
    """Incoming user request containing tasks and optimization preference weights."""

    workflow_id: str = Field(..., description="Unique identifier for the workflow execution")
    tasks: List[WorkflowTask] = Field(..., min_length=1, description="List of tasks to schedule (at least 1 required)")
    latency_importance: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Optimization weight for latency (0.0 to 1.0)",
    )
    cost_importance: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Optimization weight for cost (0.0 to 1.0)",
    )
    carbon_importance: float = Field(
        default=0.15,
        ge=0.0,
        le=1.0,
        description="Optimization weight for carbon emissions (0.0 to 1.0)",
    )
    energy_importance: float = Field(
        default=0.15,
        ge=0.0,
        le=1.0,
        description="Optimization weight for energy consumption (0.0 to 1.0)",
    )
    accuracy_importance: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
        description="Optimization weight for accuracy (0.0 to 1.0)",
    )


class ModelProfile(BaseModel):
    """Specifications, performance benchmarks, and cost/energy metrics for an AI model."""

    model_id: str = Field(..., description="Unique model identifier")
    model_name: str = Field(..., description="Human-readable display name")
    accuracy_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Benchmark accuracy score between 0.0 and 1.0",
    )
    average_latency_ms: float = Field(
        ...,
        ge=0.0,
        description="Average execution latency in milliseconds (must be >= 0)",
    )
    cost_per_1k_tokens: float = Field(
        ...,
        ge=0.0,
        description="Monetary cost per 1,000 tokens (must be >= 0)",
    )
    energy_wh_per_1k_tokens: float = Field(
        ...,
        ge=0.0,
        description="Energy consumption in Watt-hours per 1,000 tokens (must be >= 0)",
    )
    context_window: int = Field(..., gt=0, description="Maximum context window size in tokens (must be > 0)")


class RegionProfile(BaseModel):
    """Compute region profile with network latency characteristics and grid carbon intensity."""

    region_id: str = Field(..., description="Unique region identifier (e.g., us-east-1, eu-west-1)")
    region_name: str = Field(..., description="Human-readable region name")
    base_latency_ms: float = Field(
        ...,
        ge=0.0,
        description="Base network latency to the region in milliseconds (must be >= 0)",
    )
    carbon_intensity_gco2_kwh: float = Field(
        ...,
        ge=0.0,
        description="Carbon intensity of the local electrical grid in gCO2eq/kWh (must be >= 0)",
    )


class ExecutionWindow(BaseModel):
    """Time window candidate for temporal workload shifting."""

    window_id: str = Field(..., description="Unique identifier for the scheduling window")
    scheduled_offset_seconds: int = Field(
        ...,
        ge=0,
        description="Offset in seconds from the current time (must be >= 0)",
    )
    carbon_multiplier: float = Field(
        ...,
        gt=0.0,
        description="Carbon intensity multiplier relative to baseline during this window (must be > 0)",
    )


class ScheduledStep(BaseModel):
    """Scheduled assignment and resource projection for a single workflow task."""

    step_id: str = Field(..., description="Identifier of the workflow task")
    selected_model: str = Field(..., description="Model selected for execution")
    selected_region: str = Field(..., description="Region selected for execution")
    scheduled_offset_seconds: int = Field(
        ...,
        ge=0,
        description="Scheduled delay offset in seconds from submission time (must be >= 0)",
    )
    estimated_latency_ms: float = Field(
        ...,
        ge=0.0,
        description="Estimated total latency in milliseconds (must be >= 0)",
    )
    estimated_accuracy: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Estimated model accuracy score between 0.0 and 1.0",
    )
    estimated_cost: float = Field(..., ge=0.0, description="Estimated execution cost (must be >= 0)")
    estimated_energy_wh: float = Field(
        ...,
        ge=0.0,
        description="Estimated energy consumption in Watt-hours (must be >= 0)",
    )
    estimated_carbon_g: float = Field(
        ...,
        ge=0.0,
        description="Estimated carbon emissions in grams of CO2eq (must be >= 0)",
    )
    score: float = Field(..., description="Calculated composite optimization score")
    reason: str = Field(..., description="Explanation of why this model, region, and window were selected")


class ExecutionPlan(BaseModel):
    """Complete scheduled execution plan for a workflow request."""

    workflow_id: str = Field(..., description="Identifier of the associated workflow request")
    total_estimated_cost: float = Field(
        ...,
        ge=0.0,
        description="Sum of estimated costs across all steps (must be >= 0)",
    )
    total_estimated_energy_wh: float = Field(
        ...,
        ge=0.0,
        description="Sum of estimated energy consumption in Watt-hours across all steps (must be >= 0)",
    )
    total_estimated_carbon_g: float = Field(
        ...,
        ge=0.0,
        description="Sum of estimated carbon emissions in grams of CO2eq across all steps (must be >= 0)",
    )
    scheduled_steps: List[ScheduledStep] = Field(
        ...,
        description="Ordered list of scheduled steps for the workflow",
    )
