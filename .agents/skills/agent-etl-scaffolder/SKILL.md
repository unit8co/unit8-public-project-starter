---
name: agent-etl-scaffolder
description: Scaffold new agent or ETL modules in this starter without leaking business logic into the template. Use when adding registries, request/result models, placeholder services, or new starter commands.
---

# Agent ETL Scaffolder

## For new agent scaffolding

- Add typed models first.
- Register the new agent in `agentic/registry.py`.
- Keep service execution explicit about dry-run vs live-preview behavior.
- Update CLI and tests if the agent is user-accessible.

## For new ETL scaffolding

- Represent stages explicitly.
- Keep job definitions in `etl/registry.py`.
- Return structured placeholder results from `etl/service.py`.
- Add at least one smoke test for the new job path.

## Anti-patterns

- Product-specific prompts
- Hidden network calls during import
- Unexplained side effects
