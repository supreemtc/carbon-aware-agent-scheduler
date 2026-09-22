"""FastAPI application entry point for Carbon- and Latency-Aware Agent Workflow Scheduler.

Provides REST endpoints for submitting workflows, querying the simulated environment,
and checking service health.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root is in sys.path so 'backend.*' imports work from any working directory
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.gemini_planner import plan_from_text

from backend.models import (
    ExecutionPlan,
    ExecutionWindow,
    ModelProfile,
    RegionProfile,
    WorkflowRequest,
)
from backend.scheduler import compare_workflow, load_scheduler_data, schedule_workflow

app = FastAPI(
    title="Carbon- and Latency-Aware Agent Workflow Scheduler",
    description="REST API for scheduling multi-agent workflows with carbon and latency optimization.",
    version="0.1.0",
)

# CORS configuration for frontend development
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EnvironmentResponse(BaseModel):
    """Response schema for the simulated execution environment."""

    available_models: List[ModelProfile]
    available_regions: List[RegionProfile]
    execution_windows: Dict[str, List[ExecutionWindow]]


@app.get("/health", summary="Health Check")
def get_health() -> Dict[str, str]:
    """Return health status of the service."""
    return {"status": "ok"}


@app.get("/environment", response_model=EnvironmentResponse, summary="Get Execution Environment")
def get_environment() -> EnvironmentResponse:
    """Return currently available simulated models, regions, and regional carbon execution windows."""
    try:
        models, regions, windows = load_scheduler_data()
        return EnvironmentResponse(
            available_models=models,
            available_regions=regions,
            execution_windows=windows,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load environment data: {e}",
        )


@app.post("/plan", response_model=ExecutionPlan, summary="Schedule Workflow")
def plan_workflow(workflow: WorkflowRequest) -> ExecutionPlan:
    """Receive a workflow request and return an optimized execution plan."""
    try:
        return schedule_workflow(workflow)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal scheduler error: {e}",
        )


@app.post("/plan-from-text", response_model=ExecutionPlan, summary="Plan Workflow from Natural Language")
def plan_workflow_from_text(user_request: str) -> ExecutionPlan:
    """Convert a natural-language scheduling request into a WorkflowRequest, then schedule it."""
    try:
        workflow = plan_from_text(user_request)
        return schedule_workflow(workflow)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gemini planning error: {e}",
        )


@app.post("/compare", summary="Compare Optimized Schedule vs Baseline")
def compare_plan_endpoint(workflow: WorkflowRequest) -> Dict[str, Any]:
    """Receive a workflow request and return the optimized plan compared with the baseline."""
    try:
        return compare_workflow(workflow)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal comparison error: {e}",
        )
