"""Tests for OpenAI Agents SDK runtime configuration."""

from agentic_project_starter.runtime.bootstrap import build_runtime_context
from agentic_project_starter.runtime.openai import configure_openai_runtime
from agentic_project_starter.shared.config import Settings


def test_configure_openai_runtime_sets_agents_sdk_key() -> None:
    calls: list[tuple[str, bool]] = []
    settings = Settings(
        _env_file=None,
        openai_api_key="sk-test",
        openai_enable_tracing=True,
    )

    configured = configure_openai_runtime(
        settings,
        key_setter=lambda key, use_for_tracing: calls.append((key, use_for_tracing)),
    )

    assert configured is True
    assert calls == [("sk-test", True)]


def test_configure_openai_runtime_skips_missing_key() -> None:
    calls: list[tuple[str, bool]] = []
    settings = Settings(_env_file=None, openai_api_key=None)

    configured = configure_openai_runtime(
        settings,
        key_setter=lambda key, use_for_tracing: calls.append((key, use_for_tracing)),
    )

    assert configured is False
    assert calls == []


def test_runtime_context_applies_openai_configuration(monkeypatch) -> None:
    calls: list[Settings] = []

    def fake_configure_openai_runtime(settings: Settings) -> bool:
        calls.append(settings)
        return True

    monkeypatch.setattr(
        "agentic_project_starter.runtime.bootstrap.configure_openai_runtime",
        fake_configure_openai_runtime,
    )

    settings = Settings(_env_file=None, openai_api_key="sk-test")
    build_runtime_context(settings)

    assert calls == [settings]
