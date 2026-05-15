PYTHON ?= python3
UV ?= uv
PACKAGE := agentic_project_starter

.PHONY: sync lock format lint typecheck test check serve doctor agent etl quiz quiz-verify docker-build docker-up terraform-fmt terraform-validate frontend-install frontend frontend-build frontend-preview

sync:
	$(UV) sync --dev

lock:
	$(UV) lock

format:
	$(UV) run ruff format .

lint:
	$(UV) run ruff check .

typecheck:
	$(UV) run mypy src

test:
	$(UV) run pytest --cov=$(PACKAGE) --cov-report=term-missing

check: lint typecheck test

serve:
	$(UV) run agentic-starter serve

frontend-install:
	npm --prefix frontend install

frontend:
	npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173

frontend-build:
	npm --prefix frontend run build

frontend-preview:
	npm --prefix frontend run preview

doctor:
	$(UV) run agentic-starter doctor

agent:
	$(UV) run agentic-starter run-agent --agent-name coordinator --prompt "Plan a placeholder agent workflow"

etl:
	$(UV) run agentic-starter run-etl --job-name bootstrap_pipeline

quiz:
	$(UV) run agentic-starter quiz-changes --base origin/main --head HEAD

quiz-verify:
	$(UV) run agentic-starter quiz-changes --verify --base origin/main --head HEAD

docker-build:
	docker build -t agentic-project-starter .

docker-up:
	docker compose up --build

terraform-fmt:
	terraform fmt -recursive infra/terraform

terraform-validate:
	for dir in infra/terraform/environments/azure infra/terraform/environments/aws infra/terraform/environments/gcp; do \
		terraform -chdir=$$dir init -backend=false; \
		terraform -chdir=$$dir validate; \
	done
