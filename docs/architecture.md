# Architecture Overview

This repository is intentionally a scaffold rather than a product. It gives new
projects a clear starting point for:

- a Python web runtime
- OpenAI Agents SDK-based orchestration
- ETL pipelines
- an optional ChatKit-based frontend accelerator
- local and Docker execution
- multi-cloud Terraform deployment

## Source layout

- `src/agentic_project_starter/runtime`
  - runtime bootstrap, application context, and service wiring
- `src/agentic_project_starter/shared`
  - typed settings and shared helpers
- `src/agentic_project_starter/api`
  - FastAPI routes and ASGI entrypoint
- `src/agentic_project_starter/cli`
  - Typer commands for local runtime, doctor checks, agent runs, and ETL runs
- `src/agentic_project_starter/agentic`
  - starter agent registry, request/response models, and OpenAI Agents SDK stubs
- `src/agentic_project_starter/chat`
  - generic chat service seam, file-backed starter chat storage, and the optional ChatKit adapter
- `src/agentic_project_starter/etl`
  - ETL job registry and starter execution contracts
- `frontend`
  - optional Vite + React ChatKit accelerator that can be removed or replaced in downstream repos

## Runtime model

- Local execution uses `uv run agentic-starter ...`
- Container execution uses the same CLI inside Docker
- FastAPI exposes a minimal service surface:
  - `/healthz`
  - `/v1/runtime/summary`
  - `/chatkit` for the optional self-hosted chat accelerator

The runtime intentionally exposes starter metadata rather than business logic.

## Extension path

When turning this starter into a real project:

1. Replace placeholder agent registry entries with task-specific agents and tools.
2. Replace ETL stub stages with real extract/transform/load implementations.
3. Replace the file-backed chat storage and ChatKit adapter if your real project needs different UX or persistence.
4. Add domain routers and services under `api/` and `runtime/`.
5. Wire cloud-specific secrets and identity into the Terraform environment that matches your target cloud.
