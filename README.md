# agentic-project-starter

`agentic-project-starter` is a Python boilerplate for new projects that need:

- a FastAPI runtime
- OpenAI Agents SDK scaffolding
- ETL job structure
- an optional ChatKit-based frontend accelerator
- local and Docker execution
- strong Codex contributor guidance through `AGENTS.md` and repo-local skills

This repository intentionally ships placeholder workflows rather than business
logic. The goal is to give new projects a clean, opinionated starting point.

## Use This Template

This repository is meant to be used as a GitHub template, not as the final
application repo itself.

To start a new project:

1. Open this repository on GitHub.
2. Click `Use this template`.
3. Create a new repository with your project name and visibility.
4. Clone the new repository locally.
5. In the new repository, update:
   - package and module names if `agentic_project_starter` is no longer the right name
   - `.env` values and environment-variable defaults
   - README, docs, and runtime settings for the actual project
6. Commit that initial project rename and setup baseline before you start large implementation changes.

Recommended first pass in the new repo:

- decide the real product and user-facing workflow
- define the actual FastAPI routes and domain services
- replace placeholder agent definitions with project-specific agents, tools, and prompts
- replace ETL examples with real sources, transforms, and sinks
- decide whether Docker is enough for your demo or whether your project needs its own deployment setup

## How To Prompt Codex

After creating a new repo from this template, use Codex to replace the scaffold
incrementally instead of asking for one giant rewrite.

Good prompts usually include:

- the business goal and target users
- the API or CLI behavior you want
- the data sources and storage model
- the runtime target
- constraints such as auth, latency, cost, compliance, or testing expectations
- concrete acceptance criteria

When prompting Codex in the new repo:

- tell it to preserve the overall scaffold unless there is a clear reason to change structure
- ask it to implement one subsystem at a time
- ask it to update tests, docs, and env vars together when behavior changes
- be explicit about what is real logic versus what should stay as reusable template scaffolding
- if you want frontend help, say whether the product is chat-first; this starter has repo-local skills that can recommend ChatKit when that is actually a good fit

Example prompts for a new repo:

```text
Implement the real application logic for this project on top of the starter.
Keep the existing runtime/api/shared structure. Add FastAPI routes for account
creation, login, and project management, backed by PostgreSQL. Update tests,
environment variables, and docs as part of the change.
```

```text
Replace the placeholder OpenAI Agents SDK scaffolding with a real multi-agent
workflow for financial research. Keep the existing agentic package structure.
Add a coordinator, researcher, and report-writer agent, define the tools they
use, and add smoke tests for registry wiring and dry-run behavior.
```

```text
Replace the ETL starter jobs with a real pipeline that ingests CSV files from S3,
normalizes them into a warehouse-friendly schema, and writes outputs to
PostgreSQL. Keep the existing etl package structure, add typed job configs, and
update docs and environment variables.
```

```text
Design the frontend for this product on top of the starter. First decide whether
the experience should be chat-first or not. If it is chat-first, you may
recommend the optional ChatKit path in `frontend/`, but keep the backend seams
generic and replaceable. If it is not chat-first, recommend a conventional React
app structure instead. Update docs and runtime wiring only where needed.
```

## Quick start

Use this after creating a new repo from the template to validate that the
scaffold still boots correctly before you add real business logic.

```bash
cp .env.example .env
make setup
make doctor
make serve
make frontend
```

API endpoints:

- `GET /healthz`
- `GET /v1/runtime/summary`
- `POST /chatkit`

Optional frontend:

- `http://127.0.0.1:5173` during local Vite development
- same-origin frontend bundle in Docker after `docker compose up --build`

## Common commands

```bash
make setup
make doctor
make check
make serve
make frontend
make frontend-build
make agent
make etl
make quiz
make quiz-verify
make docker-up
```

## Repo layout

```text
.
├── src/agentic_project_starter
│   ├── agentic
│   ├── api
│   ├── chat
│   ├── cli
│   ├── etl
│   ├── runtime
│   └── shared
├── frontend
├── docs
└── .agents/skills
```

## Documentation

- [Architecture](docs/architecture.md)
- [Change Understanding Quiz](docs/change-quiz.md)
- [Environment Variables](docs/environment-variables.md)
- [Getting Started](docs/getting-started.md)
- [Local vs Docker](docs/local-vs-docker.md)
