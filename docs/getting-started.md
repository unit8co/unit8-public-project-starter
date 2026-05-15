# Getting Started

## 1. Initialize the project

```bash
cp .env.example .env
uv sync --dev
```

Add your `OPENAI_API_KEY` to `.env` if you plan to enable live agent runs.

## 2. Run locally

```bash
uv run agentic-starter doctor
uv run agentic-starter serve --reload
npm --prefix frontend install
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173
```

The backend stays available on `http://127.0.0.1:8000`. The optional ChatKit
frontend runs on `http://127.0.0.1:5173` and talks to the starter’s self-hosted
`/chatkit` endpoint. Add `OPENAI_API_KEY` to `.env` before sending live chat
messages.

## 3. Run placeholder workflows

```bash
uv run agentic-starter run-agent --agent-name coordinator --prompt "Draft a new project kickoff"
uv run agentic-starter run-etl --job-name bootstrap_pipeline
```

## 4. Run tests and checks

```bash
uv run ruff check .
uv run mypy src
uv run pytest --cov=agentic_project_starter
```

## 5. Run the change quiz

Use this before opening a PR. In downstream repos created from this template,
the quiz verification job runs on pull requests by default unless
`CHANGE_QUIZ_REQUIRED=false` is set in GitHub:

```bash
uv run agentic-starter quiz-changes --base origin/main --head HEAD
```

See [Change Understanding Quiz](change-quiz.md) for GitHub enforcement details.

## 6. Build and run with Docker

```bash
docker build -t agentic-project-starter .
docker compose up --build
```

In Docker mode, FastAPI serves the built frontend bundle directly from
`frontend/dist`, so the chat UI and backend share the same origin.
