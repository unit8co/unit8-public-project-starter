# Source Tree Guide

## Design Rules
- Keep imports flowing inward: API and CLI depend on runtime/shared services, not the reverse.
- Agentic and ETL packages should expose registries and service functions, not framework-specific globals.
- Keep SDK integration optional at import time when practical so smoke tests can stay lightweight.
- Prefer dataclasses and typed return models for starter registries and run results.

## Placeholder Policy
- Stub behavior is acceptable, but it must be explicit in names and user-facing output.
- Do not embed project-specific prompts, datasets, or deployment assumptions into starter modules.
