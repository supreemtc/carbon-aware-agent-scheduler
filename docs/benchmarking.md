# Benchmarking Methodology

## Baseline

Define a fixed baseline such as:

- immediate execution
- fixed model
- fixed region
- no temporal shifting

## Optimized run

Use identical workflow inputs and candidate profiles, but enable the scheduler's multi-objective optimization.

## Metrics

Record:

- total cost
- total energy
- estimated carbon
- latency
- accuracy
- scheduling delay
- selected model
- selected region
- number of feasible candidates

## Reduction

For a lower-is-better metric:

```text
reduction_pct =
    (baseline - optimized) / baseline × 100
```

## Experimental discipline

Record the:

- timestamp
- model version
- carbon data source
- region
- token estimate
- measurement method

The current repository's demo values are synthetic and should be labeled as such.
