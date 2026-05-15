---
name: observability-standards
description: Add logging and telemetry hooks that make starter workflows debuggable without pretending to be production-complete. Use when changing runtime bootstrap, ETL execution, or agent execution paths.
---

# Observability Standards

## Principles

- Configure logging centrally.
- Emit clear, low-noise operational information.
- Prefer structure and consistency over verbosity.
- Keep telemetry hooks optional and environment-driven.

## Minimums

- Log level is configurable.
- Health and runtime metadata are observable.
- Placeholder execution paths identify themselves as placeholder behavior.
