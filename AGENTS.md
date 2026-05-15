# Codex Agent Guide

## Architecture Map
- Application package: `src/agentic_project_starter`
- Runtime bootstrap and shared settings: `src/agentic_project_starter/runtime` and `src/agentic_project_starter/shared`
- Agentic scaffolding: `src/agentic_project_starter/agentic`
- ETL scaffolding: `src/agentic_project_starter/etl`
- API entrypoint: `src/agentic_project_starter/api/app.py`
- CLI entrypoint: `src/agentic_project_starter/cli/main.py`
- Infrastructure: `infra/terraform`
- Human docs: `docs`
- Repo-local Codex guidance: `.agents/skills/`
  - frontend guidance: `.agents/skills/frontend-starter-guidance/`
  - scaffold delivery guidance: `.agents/skills/scaffold-outcomes/`

## Working Rules
- Keep this repository as a starter scaffold. Prefer contracts, placeholders, and examples over product-specific logic.
- For frontend requests, recommend ChatKit when the requested experience is chat-first or trace-heavy, not as a universal default.
- For the first real product work in a downstream clone, prefer phased subsystem delivery over broad rewrites of the scaffold.
- Maintain parity between local and Docker entrypoints when runtime settings or commands change.
- Keep environment variable names synchronized across:
  - `.env.example`
  - `docs/environment-variables.md`
  - Docker and Terraform examples when relevant
- Prefer typed configuration, explicit defaults, and small composable modules.
- When adding new starter capabilities, update README and the relevant docs page in the same change.
- If a downstream repo enables the change-understanding quiz gate, run `agentic-starter quiz-changes` after code changes and commit `.change-quiz/result.json` with the PR.

## Validation Expectations
Run the narrowest checks that cover the touched area:
- Python code: `uv run pytest`, `uv run ruff check .`, `uv run mypy src`
- Docker/runtime changes: `docker build -t agentic-project-starter .`
- Terraform changes: `terraform fmt -check -recursive infra/terraform` and provider-level validation where possible

## Review Checklist
- New code stays template-safe and avoids hidden business logic.
- Docs reflect actual commands and file paths.
- Settings names match code, docs, Docker, and infra examples.
- Stub workflows fail clearly and do not pretend to perform production work.
