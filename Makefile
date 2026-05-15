UV ?= uv
PACKAGE := agentic_project_starter

.PHONY: setup format check doctor serve frontend frontend-build agent etl quiz quiz-verify docker-up

setup:
	$(UV) sync --dev
	npm --prefix frontend install

format:
	$(UV) run ruff format .

check:
	$(UV) run ruff check .
	$(UV) run mypy src
	$(UV) run pytest --cov=$(PACKAGE) --cov-report=term-missing

doctor:
	$(UV) run agentic-starter doctor

serve:
	$(UV) run agentic-starter serve --reload

frontend:
	npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173

frontend-build:
	npm --prefix frontend run build

agent:
	$(UV) run agentic-starter run-agent --agent-name coordinator --prompt "Plan a placeholder agent workflow"

etl:
	$(UV) run agentic-starter run-etl --job-name bootstrap_pipeline

quiz:
	$(UV) run agentic-starter quiz-changes --base origin/main --head HEAD

quiz-verify:
	$(UV) run agentic-starter quiz-changes --verify --base origin/main --head HEAD

docker-up:
	docker compose up --build
