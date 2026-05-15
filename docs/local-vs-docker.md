# Local And Docker Runtime

The starter keeps the same application interface in both modes.

## Local

- command: `uv run agentic-starter serve --reload`
- optional frontend: `npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173`
- configuration: `.env` and optional `.env.local`
- best for: fast iteration, smoke tests, and starter customization

## Docker

- command: `docker compose up --build`
- configuration: `.env` plus Docker environment overrides
- best for: parity checks, container validation, and cloud handoff preparation

## Runtime parity expectations

- both modes expose `/healthz`
- both modes serve the same FastAPI application
- local mode may use a separate Vite dev server for the optional ChatKit frontend
- Docker mode serves the built frontend bundle from FastAPI for one-app delivery
- both modes use the same typed settings model
- both modes support the same CLI entrypoint pattern
