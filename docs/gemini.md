# Gemini Integration

## Purpose

Gemini provides an optional natural-language interface to the scheduler.

Example:

> Run a report workflow with at least 85% accuracy. It may wait up to one minute, and carbon should matter more than cost.

Gemini converts the request into a validated `WorkflowRequest`.

The deterministic scheduler then chooses the model, region and execution window.

## Setup

Install:

```bash
pip install google-genai
```

Set:

```text
GEMINI_API_KEY=your_key
```

Optional model:

```text
GEMINI_MODEL=gemini-3.8-flash
```

## Security

Never commit the API key.

Use an environment variable or deployment secret.

## Design principle

The LLM should produce scheduling requirements, not infrastructure decisions.

This gives the system:

- natural-language usability
- structured validation
- deterministic optimization
- reproducible scheduling decisions
