# Engineering Roadmap

## Milestone 1 — Reproducible prototype

- Constraint-aware scheduling
- Pydantic validation
- FastAPI API
- Synthetic profiles
- Explainable plans
- Integration demo

## Milestone 2 — Pareto optimization

Add dominance checks and expose the non-dominated candidate set alongside the weighted selection.

## Milestone 3 — Workflow DAGs

Represent dependencies such as:

```text
ingest
  ↓
summarize ──┐
            ├──> report
reasoning ──┘
```

Scheduling must respect dependency completion and critical-path deadlines.

## Milestone 4 — Live carbon data

Create a provider interface:

```python
class CarbonIntensityProvider:
    def get_intensity(self, region_id, timestamp):
        ...
```

Implement synthetic, live and replay providers.

## Milestone 5 — Measurement

Separate estimated energy from measured energy and account for datacenter overhead where data is available.

## Milestone 6 — Closed-loop execution

```text
plan → approve → execute → observe → update → re-plan
```
