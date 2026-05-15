---
name: api-cli-parity
description: Preserve parity between FastAPI and CLI entrypoints so local, Docker, and future cloud execution use the same runtime assumptions. Use when touching runtime wiring, commands, or app bootstrap.
---

# API CLI Parity

## Principles

- API and CLI should resolve settings from the same source.
- Runtime summaries exposed in the API should stay consistent with CLI doctor output.
- Do not add one-off bootstrap logic to only one entrypoint unless the difference is intentional and documented.

## Check

- `uv run agentic-starter doctor`
- `uv run agentic-starter serve`
- `/healthz`
- `/v1/runtime/summary`
