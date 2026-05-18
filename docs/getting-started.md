# Getting Started

## 1. Initialize the project

```bash
cp .env.example .env
make setup
```

Add your `OPENAI_API_KEY` to `.env` if you plan to enable live agent runs.

## 2. Run locally

```bash
make doctor
make serve
make frontend
```

The backend stays available on `http://127.0.0.1:8000`. The optional ChatKit
frontend runs on `http://127.0.0.1:5173` and talks to the starter’s self-hosted
`/chatkit` endpoint through the Vite dev proxy. Add `OPENAI_API_KEY` to `.env`
before sending live chat messages.

## 3. Run placeholder workflows

```bash
make agent
make etl
```

## 4. Run tests and checks

```bash
make check
```

## 5. Run the change quiz

Use this before opening a PR. In downstream repos created from this template,
the quiz verification job runs on pull requests by default unless
`CHANGE_QUIZ_REQUIRED=false` is set in GitHub:

```bash
make quiz
```

See [Change Understanding Quiz](change-quiz.md) for GitHub enforcement details.

## 6. Build and run with Docker

```bash
make docker-up
```

In Docker mode, FastAPI serves the built frontend bundle directly from
`frontend/dist`, so the chat UI and backend share the same origin.
