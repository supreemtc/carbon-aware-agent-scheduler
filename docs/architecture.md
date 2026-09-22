# Architecture

## System boundary

The system has four main layers:

1. Input layer
2. Scheduling layer
3. Optimization layer
4. API layer

An optional Gemini layer converts natural-language intent into a typed workflow request before deterministic scheduling.

## Scheduling algorithm

For every task:

```text
for model in models:
    for region in regions:
        for window in region_windows:
            estimate latency
            estimate accuracy
            estimate cost
            estimate energy
            estimate carbon

            reject if accuracy < minimum_accuracy
            reject if latency > deadline

            keep feasible candidate
```

For feasible candidates:

```text
normalized(x) = (x - min(x)) / (max(x) - min(x))
```

Then:

```text
score =
    w_latency * normalized_latency
  + w_cost * normalized_cost
  + w_energy * normalized_energy
  + w_carbon * normalized_carbon
```

Lower is better.

Tie-breaking is deterministic: score, carbon, latency, cost, model ID, region ID, then window offset.

## Carbon calculation

The prototype estimates:

```text
energy_Wh =
    estimated_tokens / 1000 × model.energy_Wh_per_1k_tokens
```

and:

```text
carbon_g =
    energy_Wh / 1000
    × region.carbon_intensity_gCO2eq_per_kWh
    × window.carbon_multiplier
```

The current profiles are synthetic.

## Why this is not called Pareto yet

The implementation reduces multiple objectives to one weighted score.

A true Pareto implementation would preserve non-dominated candidates and expose the trade-off frontier. That is a planned enhancement.

## Gemini boundary

Gemini should not directly choose infrastructure placement.

```text
Natural language
      ↓
Gemini
      ↓
WorkflowRequest
      ↓
Pydantic validation
      ↓
Deterministic optimizer
      ↓
ExecutionPlan
```

This separates probabilistic language understanding from deterministic scheduling.

## Production evolution

A future deployment can replace static JSON profiles with providers:

```text
                    ┌── Model catalog / pricing
                    │
Workflow → Scheduler ── Region telemetry
                    │
                    ├── Carbon intensity provider
                    │
                    └── Execution backend
```

External measurements should be timestamped and versioned.
