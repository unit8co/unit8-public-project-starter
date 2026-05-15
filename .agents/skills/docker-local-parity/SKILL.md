---
name: docker-local-parity
description: Keep local and Docker execution aligned for this starter, including entrypoints, health endpoints, environment handling, and dependency installation. Use when changing Dockerfile, compose, runtime commands, or settings.
---

# Docker Local Parity

## Guardrails

- Docker should run the same CLI or ASGI entrypoint used locally.
- Health endpoints must behave the same in both modes.
- `.env.example` remains the baseline configuration contract.
- Avoid Docker-only behavior unless it is clearly documented.

## Checks

- `uv run agentic-starter serve`
- `docker build -t agentic-project-starter .`
- `docker compose up --build`
