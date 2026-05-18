"""OpenAI SDK runtime configuration for starter entrypoints."""

from collections.abc import Callable

from agents import set_default_openai_key

from agentic_project_starter.shared.config import Settings

OpenAIKeySetter = Callable[[str, bool], None]


def configure_openai_runtime(
    settings: Settings,
    key_setter: OpenAIKeySetter = set_default_openai_key,
) -> bool:
    """Apply OpenAI settings to the Agents SDK runtime.

    Args:
        settings: Resolved starter settings for the current process.
        key_setter: Agents SDK key setter, injectable for tests.

    Returns:
        Whether an OpenAI API key was configured.
    """

    if not settings.openai_api_key:
        return False

    key_setter(settings.openai_api_key, settings.openai_enable_tracing)
    return True
