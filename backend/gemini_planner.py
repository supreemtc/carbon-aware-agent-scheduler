"""Gemini natural-language adapter for the workflow scheduler.

The adapter converts natural-language scheduling requirements into the
existing Pydantic WorkflowRequest schema. The deterministic scheduler
remains responsible for model/region/time-window selection.

The Gemini call includes bounded retries and model fallback for transient
503/UNAVAILABLE responses.
"""

import os
import time
from typing import Any

from backend.models import WorkflowRequest


DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Stable fallback chain as of September 2026.
# The first model is used unless it returns a transient 503/UNAVAILABLE error.
DEFAULT_MODEL_FALLBACKS = (
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
)

# Keep this schema separate from WorkflowRequest because the Gemini response
# schema API does not accept Pydantic's exclusiveMinimum constraints.
GEMINI_WORKFLOW_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "workflow_id": {"type": "string"},
        "tasks": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "step_id": {"type": "string"},
                    "task_type": {"type": "string"},
                    "description": {"type": "string"},
                    "input_text": {"type": "string"},
                    "estimated_tokens": {"type": "integer", "minimum": 1},
                    "minimum_accuracy": {"type": "number", "minimum": 0, "maximum": 1},
                    "deadline_seconds": {"type": "integer", "minimum": 1},
                    "delay_tolerance_seconds": {"type": "integer", "minimum": 0},
                    "priority": {"type": "string"},
                },
                "required": [
                    "step_id",
                    "task_type",
                    "description",
                    "input_text",
                    "estimated_tokens",
                    "minimum_accuracy",
                    "deadline_seconds",
                    "delay_tolerance_seconds",
                    "priority",
                ],
            },
        },
        "latency_importance": {"type": "number", "minimum": 0, "maximum": 1},
        "cost_importance": {"type": "number", "minimum": 0, "maximum": 1},
        "carbon_importance": {"type": "number", "minimum": 0, "maximum": 1},
        "energy_importance": {"type": "number", "minimum": 0, "maximum": 1},
        "accuracy_importance": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": [
        "workflow_id",
        "tasks",
        "latency_importance",
        "cost_importance",
        "carbon_importance",
        "energy_importance",
        "accuracy_importance",
    ],
}


def build_prompt(user_request: str) -> str:
    return f"""
Convert the user's scheduling request into a valid WorkflowRequest.

Rules:
- Create one or more concrete workflow tasks.
- estimated_tokens must be a positive integer.
- minimum_accuracy must be between 0.0 and 1.0.
- deadline_seconds must be a positive integer.
- delay_tolerance_seconds must be a non-negative integer.
- priority should normally be "low", "normal", or "high".
- All optimization weights must be between 0.0 and 1.0.
- Do not choose a model, region, or execution window.
- Do not invent live carbon measurements.
- The deterministic scheduler will make infrastructure decisions.
- Convert percentages such as 90% accuracy to 0.90.
- If the user gives no explicit optimization weights, choose sensible weights
  consistent with the request and make them sum to 1.0.

User request:
{user_request}
"""


def _model_candidates() -> list[str]:
    """Return the configured model followed by safe stable fallbacks."""
    configured = os.getenv("GEMINI_MODEL")
    candidates = [configured] if configured else [DEFAULT_MODEL]
    candidates.extend(DEFAULT_MODEL_FALLBACKS)

    # Preserve order while removing duplicates.
    return list(dict.fromkeys(candidates))


def _is_transient_503(exc: Exception) -> bool:
    """Return True for Gemini errors that are reasonable to retry/fallback."""
    status = getattr(exc, "status_code", None)
    if status == 503:
        return True

    message = str(exc).upper()
    return "503" in message or "UNAVAILABLE" in message


def _generate_with_fallback(client: Any, prompt: str) -> Any:
    """Call Gemini with bounded retries and stable-model fallback."""
    max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "1"))
    retry_delay = float(os.getenv("GEMINI_RETRY_DELAY_SECONDS", "1.0"))

    last_error: Exception | None = None

    for model_index, model_name in enumerate(_model_candidates()):
        attempts = max_retries + 1

        for attempt in range(attempts):
            try:
                return client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": GEMINI_WORKFLOW_SCHEMA,
                    },
                )
            except Exception as exc:
                last_error = exc

                # Only retry/fallback transient service-unavailable errors.
                # Authentication, quota, validation, and other errors should
                # surface immediately instead of being masked.
                if not _is_transient_503(exc):
                    raise

                if attempt < attempts - 1:
                    time.sleep(retry_delay)

        # Move to the next stable model after retries are exhausted.
        if model_index < len(_model_candidates()) - 1:
            continue

    raise RuntimeError(
        "Gemini service was temporarily unavailable across all configured "
        "fallback models. Please try again later."
    ) from last_error


def plan_from_text(user_request: str) -> WorkflowRequest:
    """Convert natural-language requirements into a validated WorkflowRequest."""
    if not user_request or not user_request.strip():
        raise ValueError("user_request must not be empty.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Set it before using /plan-from-text."
        )

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "The Gemini SDK is not installed. Run: pip install google-genai"
        ) from exc

    client = genai.Client(api_key=api_key)
    response = _generate_with_fallback(client, build_prompt(user_request))

    if getattr(response, "parsed", None) is not None:
        return WorkflowRequest.model_validate(response.parsed)

    if not getattr(response, "text", None):
        raise RuntimeError("Gemini returned an empty response.")

    # Final validation is always performed by the real project schema.
    return WorkflowRequest.model_validate_json(response.text)
