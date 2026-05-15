"""Settings tests."""

from agentic_project_starter.shared.config import Settings


def test_settings_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENVIRONMENT", "ci")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5")
    monkeypatch.setenv("CHATKIT_DOMAIN_KEY", "ci-domain")

    settings = Settings()

    assert settings.app_environment == "ci"
    assert settings.openai_model == "gpt-5"
    assert settings.chatkit_domain_key == "ci-domain"
