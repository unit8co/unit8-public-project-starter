---
name: architecture-boundaries
description: Preserve clean starter architecture boundaries between shared config, runtime wiring, API, CLI, agentic modules, and ETL modules. Use when moving code or introducing new packages in src.
---

# Architecture Boundaries

## Boundaries

- `shared`: configuration and cross-cutting helpers
- `runtime`: bootstrap and application context
- `api`: HTTP layer only
- `cli`: command layer only
- `agentic`: agent registry and execution contracts
- `etl`: ETL registry and execution contracts

## Rules

- Do not let API or CLI become the home of domain logic.
- Do not import FastAPI into ETL or agent registries.
- Keep starter extension points obvious and shallow.
