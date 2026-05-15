"""API smoke tests."""

from fastapi.testclient import TestClient

from agentic_project_starter.api.app import app
from agentic_project_starter.runtime.bootstrap import create_app
from agentic_project_starter.shared.config import Settings


def test_healthcheck() -> None:
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_runtime_summary() -> None:
    client = TestClient(app)

    response = client.get("/v1/runtime/summary")

    assert response.status_code == 200
    payload = response.json()
    assert "coordinator" in payload["agents"]
    assert "bootstrap_pipeline" in payload["etl_jobs"]
    assert payload["chat_adapter"] == "chatkit"
    assert payload["chat_storage_backend"] == "file"


def test_chatkit_requires_openai_api_key() -> None:
    test_app = create_app(Settings(_env_file=None, openai_api_key=None))
    client = TestClient(test_app)

    response = client.post("/chatkit", content=b"{}")

    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]
